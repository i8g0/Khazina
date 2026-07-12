from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.models.enums import ReportStatus

if TYPE_CHECKING:
    from app.db.models.analysis import AnalysisRun
    from app.db.models.department import Department
    from app.db.models.organization import Organization, ReportingPeriod
    from app.db.models.repository import FinancialFile


class Report(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "reports"
    __table_args__ = (
        Index("ix_reports_org_type_status", "organization_id", "report_type", "status"),
        Index("ix_reports_org_published_at", "organization_id", "published_at"),
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
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_files.id", ondelete="RESTRICT"),
        nullable=True,
    )
    analysis_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=ReportStatus.DRAFT.value,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    organization: Mapped[Organization] = relationship(
        back_populates="reports",
    )
    department: Mapped[Department | None] = relationship(
        back_populates="reports",
    )
    reporting_period: Mapped[ReportingPeriod | None] = relationship(
        back_populates="reports",
    )
    source_file: Mapped[FinancialFile | None] = relationship(
        back_populates="reports",
        foreign_keys=[source_file_id],
    )
    analysis_run: Mapped[AnalysisRun | None] = relationship(
        back_populates="reports",
    )
