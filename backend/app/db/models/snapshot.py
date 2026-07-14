"""Financial Snapshot — Silver-layer immutable parsed dataset (ADR-010)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.organization import Organization, ReportingPeriod
    from app.db.models.repository import FinancialFile, ImportRecord


class FinancialSnapshot(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "financial_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "financial_file_id",
            "snapshot_version",
            name="uq_financial_snapshots_file_version",
        ),
        CheckConstraint(
            "snapshot_version >= 1",
            name="ck_financial_snapshots_version_positive",
        ),
        CheckConstraint(
            "record_count IS NULL OR record_count >= 0",
            name="ck_financial_snapshots_record_count_non_negative",
        ),
        Index(
            "ix_financial_snapshots_org_created_at",
            "organization_id",
            "created_at",
        ),
        Index(
            "ix_financial_snapshots_file_version",
            "financial_file_id",
            "snapshot_version",
        ),
    )

    financial_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_files.id", ondelete="RESTRICT"),
        nullable=False,
    )
    import_record_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("import_records.id", ondelete="SET NULL"),
        nullable=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reporting_period_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reporting_periods.id", ondelete="SET NULL"),
        nullable=True,
    )
    snapshot_version: Mapped[int] = mapped_column(Integer, nullable=False)
    parser_version: Mapped[str] = mapped_column(String(50), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(50), nullable=False)
    record_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    materialized_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    financial_file: Mapped[FinancialFile] = relationship(
        back_populates="financial_snapshots",
    )
    import_record: Mapped[ImportRecord | None] = relationship(
        back_populates="financial_snapshot",
    )
    organization: Mapped[Organization] = relationship(
        back_populates="financial_snapshots",
    )
    reporting_period: Mapped[ReportingPeriod | None] = relationship(
        back_populates="financial_snapshots",
    )
