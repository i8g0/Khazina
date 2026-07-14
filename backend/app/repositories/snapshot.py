from __future__ import annotations

import uuid

from sqlalchemy import func, select

from app.db.models import FinancialSnapshot
from app.repositories.base import BaseRepository


class FinancialSnapshotRepository(BaseRepository):
    """Immutable Financial Snapshot persistence (ADR-010 Silver layer)."""

    def create_snapshot(self, snapshot: FinancialSnapshot) -> FinancialSnapshot:
        return self._add(snapshot)

    def get_snapshot(self, snapshot_id: uuid.UUID) -> FinancialSnapshot | None:
        return self._get(FinancialSnapshot, snapshot_id)

    def get_snapshot_by_file_version(
        self,
        financial_file_id: uuid.UUID,
        snapshot_version: int,
    ) -> FinancialSnapshot | None:
        stmt = select(FinancialSnapshot).where(
            FinancialSnapshot.financial_file_id == financial_file_id,
            FinancialSnapshot.snapshot_version == snapshot_version,
        )
        return self._session.scalars(stmt).first()

    def list_snapshots_for_file(
        self,
        financial_file_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[FinancialSnapshot]:
        stmt = self._paginate(
            select(FinancialSnapshot)
            .where(FinancialSnapshot.financial_file_id == financial_file_id)
            .order_by(FinancialSnapshot.snapshot_version.desc()),
            limit,
            offset,
        )
        return self._list(stmt)

    def get_latest_snapshot_for_file(
        self, financial_file_id: uuid.UUID
    ) -> FinancialSnapshot | None:
        stmt = (
            select(FinancialSnapshot)
            .where(FinancialSnapshot.financial_file_id == financial_file_id)
            .order_by(FinancialSnapshot.snapshot_version.desc())
            .limit(1)
        )
        return self._session.scalars(stmt).first()

    def next_snapshot_version(self, financial_file_id: uuid.UUID) -> int:
        stmt = select(func.max(FinancialSnapshot.snapshot_version)).where(
            FinancialSnapshot.financial_file_id == financial_file_id
        )
        current = self._session.scalar(stmt)
        return 1 if current is None else int(current) + 1
