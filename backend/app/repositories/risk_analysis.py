from __future__ import annotations

import uuid

from typing import Any

from sqlalchemy import select

from app.db.models import RiskAnalysisResult, RiskFinding
from app.repositories.base import BaseRepository


class RiskAnalysisRepository(BaseRepository):
    """Data access for risk analysis results and findings."""

    def create_result(self, result: RiskAnalysisResult) -> RiskAnalysisResult:
        return self._add(result)

    def get_result(self, result_id: uuid.UUID) -> RiskAnalysisResult | None:
        return self._get(RiskAnalysisResult, result_id)

    def get_result_for_run(
        self, analysis_run_id: uuid.UUID
    ) -> RiskAnalysisResult | None:
        stmt = select(RiskAnalysisResult).where(
            RiskAnalysisResult.analysis_run_id == analysis_run_id
        )
        return self._session.scalars(stmt).first()

    def add_findings(self, findings: list[RiskFinding]) -> list[RiskFinding]:
        if not findings:
            return []
        return self._add_all(findings)

    def get_finding(self, finding_id: uuid.UUID) -> RiskFinding | None:
        return self._get(RiskFinding, finding_id)

    def update_finding(
        self, finding: RiskFinding, values: dict[str, Any]
    ) -> RiskFinding:
        return self._update(finding, values)

    def list_findings(
        self,
        analysis_run_id: uuid.UUID,
        *,
        priority: str | None = None,
        category_code: str | None = None,
        finding_status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[RiskFinding]:
        stmt = select(RiskFinding).where(
            RiskFinding.analysis_run_id == analysis_run_id
        )
        if priority is not None:
            stmt = stmt.where(RiskFinding.priority == priority)
        if category_code is not None:
            stmt = stmt.where(RiskFinding.category_code == category_code)
        if finding_status is not None:
            stmt = stmt.where(RiskFinding.finding_status == finding_status)
        stmt = stmt.order_by(
            RiskFinding.score.desc(),
            RiskFinding.category_code,
            RiskFinding.name,
        )
        stmt = self._paginate(stmt, limit, offset)
        return self._list(stmt)
