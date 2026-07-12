from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.models.enums import ImportStatus, ProcessingStatus, UploadSource

if TYPE_CHECKING:
    from app.db.models.analysis import AnalysisRun
    from app.db.models.department import Department
    from app.db.models.organization import Organization, ReportingPeriod
    from app.db.models.reporting import Report


class FinancialFile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "financial_files"
    __table_args__ = (
        CheckConstraint(
            "size_bytes IS NULL OR size_bytes >= 0",
            name="ck_financial_files_size_bytes_non_negative",
        ),
        Index("ix_financial_files_org_status", "organization_id", "processing_status"),
        Index("ix_financial_files_org_uploaded_at", "organization_id", "uploaded_at"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    reporting_period_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reporting_periods.id", ondelete="SET NULL"),
        nullable=True,
    )
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    size_display: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    processing_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=ProcessingStatus.PENDING.value,
    )
    upload_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=UploadSource.REPOSITORY.value,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    file_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    organization: Mapped[Organization] = relationship(
        back_populates="financial_files",
    )
    department: Mapped[Department | None] = relationship(
        back_populates="financial_files",
    )
    reporting_period: Mapped[ReportingPeriod | None] = relationship(
        back_populates="financial_files",
    )
    import_records: Mapped[list[ImportRecord]] = relationship(
        back_populates="financial_file",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    analysis_runs: Mapped[list[AnalysisRun]] = relationship(
        back_populates="source_file",
        foreign_keys="AnalysisRun.source_file_id",
    )
    reports: Mapped[list[Report]] = relationship(
        back_populates="source_file",
        foreign_keys="Report.source_file_id",
    )


class ImportRecord(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "import_records"
    __table_args__ = (
        CheckConstraint(
            "record_count IS NULL OR record_count >= 0",
            name="ck_import_records_record_count_non_negative",
        ),
        CheckConstraint(
            "status <> 'failed' OR error_message IS NOT NULL",
            name="ck_import_records_failed_requires_error_message",
        ),
        Index(
            "ix_import_records_file_imported_at",
            "financial_file_id",
            "imported_at",
        ),
    )

    financial_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_files.id", ondelete="CASCADE"),
        nullable=False,
    )
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    record_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    financial_file: Mapped[FinancialFile] = relationship(
        back_populates="import_records",
    )


class DataQualitySnapshot(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "data_quality_snapshots"

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
    overall_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    organization: Mapped[Organization] = relationship(
        back_populates="data_quality_snapshots",
    )
    reporting_period: Mapped[ReportingPeriod | None] = relationship(
        back_populates="data_quality_snapshots",
    )
    checks: Mapped[list[DataQualityCheck]] = relationship(
        back_populates="snapshot",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DataQualityCheck(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "data_quality_checks"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_quality_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )
    check_name: Mapped[str] = mapped_column(String(200), nullable=False)
    result_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )

    snapshot: Mapped[DataQualitySnapshot] = relationship(
        back_populates="checks",
    )
