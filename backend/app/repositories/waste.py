from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.db.models import (
    WasteAnalysisResult,
    WasteCategoryBreakdown,
    WasteTrendPoint,
    WasteVendorFinding,
)
from app.repositories.base import BaseRepository


class WasteRepository(BaseRepository):
    """Data access for the Financial Waste Detection domain
    (results, category breakdowns, vendor findings, trend points)."""

    # -- analysis results (1:1 with analysis run) ---------------------------

    def create_result(self, result: WasteAnalysisResult) -> WasteAnalysisResult:
        return self._add(result)

    def get_result(self, result_id: uuid.UUID) -> WasteAnalysisResult | None:
        return self._get(WasteAnalysisResult, result_id)

    def get_result_for_run(
        self, analysis_run_id: uuid.UUID
    ) -> WasteAnalysisResult | None:
        stmt = select(WasteAnalysisResult).where(
            WasteAnalysisResult.analysis_run_id == analysis_run_id
        )
        return self._session.scalars(stmt).first()

    # -- category breakdowns -------------------------------------------------

    def add_category_breakdowns(
        self, breakdowns: list[WasteCategoryBreakdown]
    ) -> list[WasteCategoryBreakdown]:
        return self._add_all(breakdowns)

    def list_category_breakdowns(
        self,
        analysis_run_id: uuid.UUID,
        *,
        department_id: uuid.UUID | None = None,
    ) -> list[WasteCategoryBreakdown]:
        """Waste page breakdown, optionally filtered by department (design §9)."""
        stmt = select(WasteCategoryBreakdown).where(
            WasteCategoryBreakdown.analysis_run_id == analysis_run_id
        )
        if department_id is not None:
            stmt = stmt.where(WasteCategoryBreakdown.department_id == department_id)
        stmt = stmt.order_by(WasteCategoryBreakdown.display_order)
        return self._list(stmt)

    # -- vendor findings -------------------------------------------------------

    def add_vendor_findings(
        self, findings: list[WasteVendorFinding]
    ) -> list[WasteVendorFinding]:
        return self._add_all(findings)

    def list_vendor_findings(
        self,
        analysis_run_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[WasteVendorFinding]:
        stmt = self._paginate(
            select(WasteVendorFinding)
            .where(WasteVendorFinding.analysis_run_id == analysis_run_id)
            .order_by(WasteVendorFinding.amount.desc()),
            limit,
            offset,
        )
        return self._list(stmt)

    # -- trend points ------------------------------------------------------------

    def create_trend_point(self, point: WasteTrendPoint) -> WasteTrendPoint:
        return self._add(point)

    def get_trend_point(
        self,
        organization_id: uuid.UUID,
        reporting_period_id: uuid.UUID | None,
        month_label: str,
    ) -> WasteTrendPoint | None:
        """Lookup by the unique (org, period, month) key for update-on-reanalysis."""
        stmt = select(WasteTrendPoint).where(
            WasteTrendPoint.organization_id == organization_id,
            WasteTrendPoint.month_label == month_label,
        )
        if reporting_period_id is None:
            stmt = stmt.where(WasteTrendPoint.reporting_period_id.is_(None))
        else:
            stmt = stmt.where(
                WasteTrendPoint.reporting_period_id == reporting_period_id
            )
        return self._session.scalars(stmt).first()

    def list_trend_points(
        self,
        organization_id: uuid.UUID,
        *,
        reporting_period_id: uuid.UUID | None = None,
    ) -> list[WasteTrendPoint]:
        stmt = select(WasteTrendPoint).where(
            WasteTrendPoint.organization_id == organization_id
        )
        if reporting_period_id is not None:
            stmt = stmt.where(
                WasteTrendPoint.reporting_period_id == reporting_period_id
            )
        stmt = stmt.order_by(WasteTrendPoint.month_order)
        return self._list(stmt)

    def update_trend_point(
        self, point: WasteTrendPoint, values: dict[str, Any]
    ) -> WasteTrendPoint:
        return self._update(point, values)
