"""Financial Risk analysis orchestration and Gold persistence (Sprint 9.3)."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models import AnalysisRun, RiskAnalysisResult, RiskFinding
from app.db.models.enums import AnalysisType
from app.decision.mappers.risk_gold import RiskGoldMapper
from app.decision.service import DecisionService, RiskDecisionExecutionOutcome
from app.observability.structured_log import log_pipeline_event
from app.repositories import (
    AnalysisRepository,
    OrganizationRepository,
    RiskAnalysisRepository,
)
from app.services.analysis import AnalysisService
from app.services.base import BaseService
from app.services.exceptions import (
    DuplicateResourceError,
    InvalidStateError,
    ResourceNotFoundError,
)

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class RiskAnalysisExecutionOutcome:
    """Successful execute path: run, engine outcome, and persisted Gold rows."""

    analysis_run: AnalysisRun
    result: RiskAnalysisResult
    findings: tuple[RiskFinding, ...]
    decision_outcome: RiskDecisionExecutionOutcome


class RiskAnalysisService(BaseService):
    """Execute risk analyses and persist deterministic findings."""

    def __init__(
        self,
        session: Session,
        risk_analysis_repository: RiskAnalysisRepository,
        analysis_repository: AnalysisRepository,
        organization_repository: OrganizationRepository,
        analysis_service: AnalysisService,
        decision_service: DecisionService,
    ) -> None:
        super().__init__(session)
        self._risk_analysis = risk_analysis_repository
        self._analyses = analysis_repository
        self._organizations = organization_repository
        self._analysis = analysis_service
        self._decision = decision_service

    def execute(
        self,
        organization_id: uuid.UUID,
        *,
        title: str,
        source_file_id: uuid.UUID,
        source_snapshot_id: uuid.UUID | None = None,
        snapshot_version: int | None = None,
        reporting_period_id: uuid.UUID | None = None,
        initiating_user_id: uuid.UUID | None = None,
    ) -> RiskAnalysisExecutionOutcome:
        """Run RiskEngine via DecisionService and persist Gold entities."""
        started = time.perf_counter()
        decision_outcome = self._decision.execute_risk_analysis(
            organization_id,
            title=title,
            source_file_id=source_file_id,
            source_snapshot_id=source_snapshot_id,
            snapshot_version=snapshot_version,
            reporting_period_id=reporting_period_id,
            initiating_user_id=initiating_user_id,
        )
        run = decision_outcome.analysis_run
        if self._risk_analysis.get_result_for_run(run.id) is not None:
            raise DuplicateResourceError(
                f"Analysis run '{run.id}' already has a risk analysis result"
            )

        payload = RiskGoldMapper.to_persistence_payload(
            decision_outcome.engine_output,
            organization_id=organization_id,
            analysis_run_id=run.id,
            source_snapshot_id=decision_outcome.snapshot.id,
        )
        result = RiskAnalysisResult(**payload["result"])
        findings = [RiskFinding(**row) for row in payload["findings"]]

        with self._transaction():
            self._risk_analysis.create_result(result)
            persisted_findings = self._risk_analysis.add_findings(findings)

        log_pipeline_event(
            logger,
            "risk_gold_persisted",
            organization_id=str(organization_id),
            analysis_run_id=str(run.id),
            snapshot_id=str(decision_outcome.snapshot.id),
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
            finding_count=len(persisted_findings),
            posture_level=result.overall_posture_level,
        )
        return RiskAnalysisExecutionOutcome(
            analysis_run=run,
            result=result,
            findings=tuple(persisted_findings),
            decision_outcome=decision_outcome,
        )

    def list_runs(
        self,
        organization_id: uuid.UUID,
        *,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AnalysisRun]:
        return self._analysis.list_runs(
            organization_id,
            analysis_type=AnalysisType.RISK,
            status=status,
            limit=limit,
            offset=offset,
        )

    def get_run_detail(
        self, organization_id: uuid.UUID, run_id: uuid.UUID
    ) -> tuple[AnalysisRun, RiskAnalysisResult | None]:
        run = self._risk_run(organization_id, run_id)
        result = self._risk_analysis.get_result_for_run(run.id)
        return run, result

    def get_result(
        self, organization_id: uuid.UUID, run_id: uuid.UUID
    ) -> RiskAnalysisResult:
        run = self._risk_run(organization_id, run_id)
        result = self._risk_analysis.get_result_for_run(run.id)
        if result is None:
            raise ResourceNotFoundError("RiskAnalysisResult", run_id)
        return result

    def list_findings(
        self,
        organization_id: uuid.UUID,
        run_id: uuid.UUID,
        *,
        priority: str | None = None,
        category_code: str | None = None,
        finding_status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[RiskFinding]:
        run = self._risk_run(organization_id, run_id)
        return self._risk_analysis.list_findings(
            run.id,
            priority=priority,
            category_code=category_code,
            finding_status=finding_status,
            limit=limit,
            offset=offset,
        )

    def get_finding(
        self,
        organization_id: uuid.UUID,
        run_id: uuid.UUID,
        finding_id: uuid.UUID,
    ) -> RiskFinding:
        run = self._risk_run(organization_id, run_id)
        finding = self._risk_analysis.get_finding(finding_id)
        if finding is None or finding.analysis_run_id != run.id:
            raise ResourceNotFoundError("RiskFinding", finding_id)
        self._check_ownership(finding, "RiskFinding", organization_id)
        return finding

    def build_result_summary(
        self, result: RiskAnalysisResult | None
    ) -> dict[str, Any] | None:
        if result is None:
            return None
        return {
            "result_id": result.id,
            "total_findings": result.total_findings,
            "high_priority_count": result.high_priority_count,
            "medium_priority_count": result.medium_priority_count,
            "low_priority_count": result.low_priority_count,
            "overall_posture_level": result.overall_posture_level,
            "top_category_code": result.top_category_code,
            "facts_contract_version": result.facts_contract_version,
            "source_snapshot_id": result.source_snapshot_id,
        }

    def _risk_run(
        self, organization_id: uuid.UUID, run_id: uuid.UUID
    ) -> AnalysisRun:
        run = self._analyses.get(run_id)
        if run is None:
            raise ResourceNotFoundError("AnalysisRun", run_id)
        self._check_ownership(run, "AnalysisRun", organization_id)
        if run.analysis_type != AnalysisType.RISK:
            raise InvalidStateError(
                "Risk analysis endpoints require 'risk' runs "
                f"(run type: '{run.analysis_type}')"
            )
        return run

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
