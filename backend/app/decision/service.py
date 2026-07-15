"""Decision Engine orchestration — Snapshot → Business Engine → Gold (Sprint 6.3)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.business.engines.waste.manifest import ENGINE_ID
from app.business.exceptions import EngineError
from app.business.facts.contract import FactsContract
from app.business.registry import get_engine
from app.db.models import AnalysisRun, FinancialSnapshot
from app.db.models.enums import AnalysisType, ProcessingStatus
from app.decision.adapters.waste_v1 import WasteSnapshotAdapterV1
from app.decision.exceptions import SnapshotAdapterError
from app.decision.mappers.waste_gold import WasteGoldMapper
from app.repositories import (
    AnalysisRepository,
    FinancialRepository,
    FinancialSnapshotRepository,
    OrganizationRepository,
)
from app.services.analysis import AnalysisService
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    InvalidStateError,
    ResourceNotFoundError,
)
from app.services.waste import WasteService


@dataclass(frozen=True, slots=True)
class DecisionExecutionOutcome:
    """Result of a successful waste decision execution."""

    analysis_run: AnalysisRun
    facts_contract: FactsContract
    snapshot: FinancialSnapshot


class DecisionService(BaseService):
    """Deterministic Silver-to-Gold decision path without AI."""

    def __init__(
        self,
        session: Session,
        analysis_service: AnalysisService,
        waste_service: WasteService,
        snapshot_repository: FinancialSnapshotRepository,
        financial_repository: FinancialRepository,
        organization_repository: OrganizationRepository,
        analysis_repository: AnalysisRepository,
        *,
        waste_adapter: WasteSnapshotAdapterV1 | None = None,
    ) -> None:
        super().__init__(session)
        self._analysis = analysis_service
        self._waste = waste_service
        self._snapshots = snapshot_repository
        self._financials = financial_repository
        self._organizations = organization_repository
        self._analyses = analysis_repository
        self._waste_adapter = waste_adapter or WasteSnapshotAdapterV1()

    def execute_waste_analysis(
        self,
        organization_id: uuid.UUID,
        *,
        title: str,
        source_file_id: uuid.UUID,
        source_snapshot_id: uuid.UUID | None = None,
        snapshot_version: int | None = None,
        reporting_period_id: uuid.UUID | None = None,
        initiating_user_id: uuid.UUID | None = None,
    ) -> DecisionExecutionOutcome:
        """End-to-end waste decision: snapshot → engine → Gold persistence."""
        if snapshot_version is not None and source_snapshot_id is not None:
            raise BusinessValidationError(
                "Provide either source_snapshot_id or snapshot_version, not both"
            )

        source_file = self._financials.get_file(source_file_id)
        if source_file is None:
            raise ResourceNotFoundError("FinancialFile", source_file_id)
        self._check_ownership(source_file, "FinancialFile", organization_id)
        if source_file.processing_status != ProcessingStatus.READY_FOR_ANALYSIS:
            raise InvalidStateError(
                "Source file must be ready for analysis before decision execution "
                f"(current status: '{source_file.processing_status}')"
            )

        snapshot = self._resolve_snapshot(
            organization_id,
            source_file_id,
            source_snapshot_id=source_snapshot_id,
            snapshot_version=snapshot_version,
        )
        period_label = self._resolve_period_label(snapshot, reporting_period_id)

        run = self._analysis.create_run(
            organization_id,
            analysis_type=AnalysisType.FINANCIAL_WASTE,
            title=title,
            source_file_id=source_file_id,
            source_snapshot_id=snapshot.id,
            reporting_period_id=reporting_period_id or snapshot.reporting_period_id,
            runtime_metadata={
                "decision_engine": "waste_v1",
                "snapshot_version": snapshot.snapshot_version,
            },
        )
        self._analysis.start_run(organization_id, run.id)

        try:
            engine_input = self._waste_adapter.adapt(
                snapshot.payload,
                organization_id=str(organization_id),
                period=period_label,
            )
            engine = get_engine(ENGINE_ID)
            facts = engine.run(engine_input)
            gold_payload = WasteGoldMapper.to_record_payload(facts)
            self._waste.record_result(organization_id, run.id, **gold_payload)
            completed = self._analysis.complete_run(
                organization_id,
                run.id,
                success_metadata={"facts_contract": facts.to_dict()},
                initiating_user_id=initiating_user_id,
            )
        except SnapshotAdapterError as exc:
            self._analysis.fail_run(
                organization_id,
                run.id,
                failure_details=exc.to_failure_details(),
            )
            raise
        except EngineError as exc:
            self._analysis.fail_run(
                organization_id,
                run.id,
                failure_details={
                    "error_code": "engine_execution_failed",
                    "message": str(exc),
                },
            )
            raise

        return DecisionExecutionOutcome(
            analysis_run=completed,
            facts_contract=facts,
            snapshot=snapshot,
        )

    def _resolve_snapshot(
        self,
        organization_id: uuid.UUID,
        source_file_id: uuid.UUID,
        *,
        source_snapshot_id: uuid.UUID | None,
        snapshot_version: int | None,
    ) -> FinancialSnapshot:
        if source_snapshot_id is not None:
            snapshot = self._snapshots.get_snapshot(source_snapshot_id)
            if snapshot is None:
                raise ResourceNotFoundError("FinancialSnapshot", source_snapshot_id)
        elif snapshot_version is not None:
            snapshot = self._snapshots.get_snapshot_by_file_version(
                source_file_id, snapshot_version
            )
            if snapshot is None:
                raise ResourceNotFoundError(
                    "FinancialSnapshot",
                    f"{source_file_id}:v{snapshot_version}",
                )
        else:
            snapshot = self._snapshots.get_latest_snapshot_for_file(source_file_id)
            if snapshot is None:
                raise ResourceNotFoundError(
                    "FinancialSnapshot",
                    f"latest for file {source_file_id}",
                )

        self._check_ownership(snapshot, "FinancialSnapshot", organization_id)
        if snapshot.financial_file_id != source_file_id:
            raise BusinessValidationError(
                "Snapshot does not belong to the requested source file"
            )
        return snapshot

    def _resolve_period_label(
        self,
        snapshot: FinancialSnapshot,
        reporting_period_id: uuid.UUID | None,
    ) -> str | None:
        period_id = reporting_period_id or snapshot.reporting_period_id
        if period_id is None:
            return None
        period = self._organizations.get_reporting_period(period_id)
        if period is None:
            return None
        return period.label
