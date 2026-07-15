"""Report export store data access."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.db.models.report_export import ReportExport
from app.repositories.base import BaseRepository


class ReportExportRepository(BaseRepository):
    """Persistence for binary report export records."""

    def create(self, export_record: ReportExport) -> ReportExport:
        return self._add(export_record)

    def get_by_dedup_key(
        self,
        report_id: uuid.UUID,
        export_format: str,
        content_fingerprint: str,
        preferences_fingerprint: str,
    ) -> ReportExport | None:
        stmt = select(ReportExport).where(
            ReportExport.report_id == report_id,
            ReportExport.export_format == export_format,
            ReportExport.content_fingerprint == content_fingerprint,
            ReportExport.preferences_fingerprint == preferences_fingerprint,
        )
        return self._session.scalars(stmt).first()

    def get(self, export_id: uuid.UUID) -> ReportExport | None:
        return self._get(ReportExport, export_id)
