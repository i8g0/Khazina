from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.db.models import Report
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository):
    """Data access for the Executive Reporting domain (published report catalog)."""

    def create(self, report: Report) -> Report:
        return self._add(report)

    def get(self, report_id: uuid.UUID) -> Report | None:
        return self._get(Report, report_id)

    def require(self, report_id: uuid.UUID) -> Report:
        return self._require(Report, report_id)

    def list_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        report_type: str | None = None,
        status: str | None = None,
        department_id: uuid.UUID | None = None,
        reporting_period_id: uuid.UUID | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Report]:
        """Reports page filters (type/department/period), newest first (design §9)."""
        stmt = select(Report).where(Report.organization_id == organization_id)
        if report_type is not None:
            stmt = stmt.where(Report.report_type == report_type)
        if status is not None:
            stmt = stmt.where(Report.status == status)
        if department_id is not None:
            stmt = stmt.where(Report.department_id == department_id)
        if reporting_period_id is not None:
            stmt = stmt.where(Report.reporting_period_id == reporting_period_id)
        stmt = self._paginate(
            stmt.order_by(Report.published_at.desc().nulls_last()), limit, offset
        )
        return self._list(stmt)

    def count_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        report_type: str | None = None,
        status: str | None = None,
    ) -> int:
        stmt = select(Report).where(Report.organization_id == organization_id)
        if report_type is not None:
            stmt = stmt.where(Report.report_type == report_type)
        if status is not None:
            stmt = stmt.where(Report.status == status)
        return self._count(stmt)

    def update(self, report: Report, values: dict[str, Any]) -> Report:
        return self._update(report, values)

    def delete(self, report: Report) -> None:
        self._delete(report)
