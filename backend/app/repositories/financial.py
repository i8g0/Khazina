from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.db.models import (
    DataQualityCheck,
    DataQualitySnapshot,
    FinancialFile,
    ImportRecord,
)
from app.repositories.base import BaseRepository


class FinancialRepository(BaseRepository):
    """Data access for the Financial Data Repository domain
    (files, import records, data quality snapshots and checks)."""

    # -- financial files ---------------------------------------------------

    def create_file(self, financial_file: FinancialFile) -> FinancialFile:
        return self._add(financial_file)

    def get_file(self, file_id: uuid.UUID) -> FinancialFile | None:
        return self._get(FinancialFile, file_id)

    def require_file(self, file_id: uuid.UUID) -> FinancialFile:
        return self._require(FinancialFile, file_id)

    def list_files(
        self,
        organization_id: uuid.UUID,
        *,
        processing_status: str | None = None,
        upload_source: str | None = None,
        department_id: uuid.UUID | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[FinancialFile]:
        """Data Management file list, most recently uploaded first (design §9)."""
        stmt = select(FinancialFile).where(
            FinancialFile.organization_id == organization_id
        )
        if processing_status is not None:
            stmt = stmt.where(FinancialFile.processing_status == processing_status)
        if upload_source is not None:
            stmt = stmt.where(FinancialFile.upload_source == upload_source)
        if department_id is not None:
            stmt = stmt.where(FinancialFile.department_id == department_id)
        stmt = self._paginate(
            stmt.order_by(FinancialFile.uploaded_at.desc()), limit, offset
        )
        return self._list(stmt)

    def count_files(
        self,
        organization_id: uuid.UUID,
        *,
        processing_status: str | None = None,
    ) -> int:
        stmt = select(FinancialFile).where(
            FinancialFile.organization_id == organization_id
        )
        if processing_status is not None:
            stmt = stmt.where(FinancialFile.processing_status == processing_status)
        return self._count(stmt)

    def update_file(
        self, financial_file: FinancialFile, values: dict[str, Any]
    ) -> FinancialFile:
        return self._update(financial_file, values)

    def delete_file(self, financial_file: FinancialFile) -> None:
        """Deletes the file row; import records cascade, analyses RESTRICT at DB level."""
        self._delete(financial_file)

    # -- import records (append-only) ---------------------------------------

    def add_import_record(self, record: ImportRecord) -> ImportRecord:
        return self._add(record)

    def get_import_record(self, record_id: uuid.UUID) -> ImportRecord | None:
        return self._get(ImportRecord, record_id)

    def list_import_records(
        self,
        financial_file_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ImportRecord]:
        stmt = self._paginate(
            select(ImportRecord)
            .where(ImportRecord.financial_file_id == financial_file_id)
            .order_by(ImportRecord.imported_at.desc()),
            limit,
            offset,
        )
        return self._list(stmt)

    # -- data quality snapshots and checks -----------------------------------

    def create_snapshot(self, snapshot: DataQualitySnapshot) -> DataQualitySnapshot:
        return self._add(snapshot)

    def get_snapshot(self, snapshot_id: uuid.UUID) -> DataQualitySnapshot | None:
        return self._get(DataQualitySnapshot, snapshot_id)

    def get_latest_snapshot(
        self,
        organization_id: uuid.UUID,
        *,
        reporting_period_id: uuid.UUID | None = None,
    ) -> DataQualitySnapshot | None:
        """Latest snapshot supersedes display; historical rows retained (design §3.3)."""
        stmt = select(DataQualitySnapshot).where(
            DataQualitySnapshot.organization_id == organization_id
        )
        if reporting_period_id is not None:
            stmt = stmt.where(
                DataQualitySnapshot.reporting_period_id == reporting_period_id
            )
        stmt = stmt.order_by(DataQualitySnapshot.evaluated_at.desc()).limit(1)
        return self._session.scalars(stmt).first()

    def add_checks(self, checks: list[DataQualityCheck]) -> list[DataQualityCheck]:
        return self._add_all(checks)

    def list_checks(self, snapshot_id: uuid.UUID) -> list[DataQualityCheck]:
        stmt = (
            select(DataQualityCheck)
            .where(DataQualityCheck.snapshot_id == snapshot_id)
            .order_by(DataQualityCheck.display_order)
        )
        return self._list(stmt)
