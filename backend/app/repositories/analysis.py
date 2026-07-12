from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.db.models import AnalysisRun
from app.repositories.base import BaseRepository


class AnalysisRepository(BaseRepository):
    """Data access for the shared Analysis domain (analysis runs)."""

    def create(self, run: AnalysisRun) -> AnalysisRun:
        return self._add(run)

    def get(self, run_id: uuid.UUID) -> AnalysisRun | None:
        return self._get(AnalysisRun, run_id)

    def require(self, run_id: uuid.UUID) -> AnalysisRun:
        return self._require(AnalysisRun, run_id)

    def list_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        analysis_type: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AnalysisRun]:
        """Recent-analyses listing, newest first (design §9)."""
        stmt = select(AnalysisRun).where(
            AnalysisRun.organization_id == organization_id
        )
        if analysis_type is not None:
            stmt = stmt.where(AnalysisRun.analysis_type == analysis_type)
        if status is not None:
            stmt = stmt.where(AnalysisRun.status == status)
        stmt = self._paginate(
            stmt.order_by(AnalysisRun.created_at.desc()), limit, offset
        )
        return self._list(stmt)

    def list_recent_completed(
        self, organization_id: uuid.UUID, *, limit: int
    ) -> list[AnalysisRun]:
        """Completed runs ordered by completion time for dashboard/timeline views."""
        stmt = (
            select(AnalysisRun)
            .where(
                AnalysisRun.organization_id == organization_id,
                AnalysisRun.completed_at.is_not(None),
            )
            .order_by(AnalysisRun.completed_at.desc())
            .limit(limit)
        )
        return self._list(stmt)

    def list_for_file(self, source_file_id: uuid.UUID) -> list[AnalysisRun]:
        stmt = (
            select(AnalysisRun)
            .where(AnalysisRun.source_file_id == source_file_id)
            .order_by(AnalysisRun.created_at.desc())
        )
        return self._list(stmt)

    def count_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        analysis_type: str | None = None,
        status: str | None = None,
    ) -> int:
        stmt = select(AnalysisRun).where(
            AnalysisRun.organization_id == organization_id
        )
        if analysis_type is not None:
            stmt = stmt.where(AnalysisRun.analysis_type == analysis_type)
        if status is not None:
            stmt = stmt.where(AnalysisRun.status == status)
        return self._count(stmt)

    def update(self, run: AnalysisRun, values: dict[str, Any]) -> AnalysisRun:
        return self._update(run, values)

    def delete(self, run: AnalysisRun) -> None:
        """Deletes the run; domain result rows cascade at DB level."""
        self._delete(run)
