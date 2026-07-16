from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.models.enums import AnalysisRunStatus

if TYPE_CHECKING:
    from app.db.models.organization import Organization, ReportingPeriod
    from app.db.models.recommendation import Recommendation
    from app.db.models.repository import FinancialFile
    from app.db.models.reporting import Report
    from app.db.models.risk_analysis import RiskAnalysisResult, RiskFinding
    from app.db.models.simulation import SimulationRun
    from app.db.models.snapshot import FinancialSnapshot
    from app.db.models.waste import (
        WasteAnalysisResult,
        WasteCategoryBreakdown,
        WasteVendorFinding,
    )


class AnalysisRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "analysis_runs"
    __table_args__ = (
        Index(
            "ix_analysis_runs_org_type_status",
            "organization_id",
            "analysis_type",
            "status",
        ),
        Index("ix_analysis_runs_source_file_id", "source_file_id"),
        Index("ix_analysis_runs_source_snapshot_id", "source_snapshot_id"),
        Index("ix_analysis_runs_org_completed_at", "organization_id", "completed_at"),
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
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_files.id", ondelete="RESTRICT"),
        nullable=True,
    )
    source_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_snapshots.id", ondelete="RESTRICT"),
        nullable=True,
    )
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=AnalysisRunStatus.PENDING.value,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    runtime_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    organization: Mapped[Organization] = relationship(
        back_populates="analysis_runs",
    )
    reporting_period: Mapped[ReportingPeriod | None] = relationship(
        back_populates="analysis_runs",
    )
    source_file: Mapped[FinancialFile | None] = relationship(
        back_populates="analysis_runs",
        foreign_keys=[source_file_id],
    )
    source_snapshot: Mapped[FinancialSnapshot | None] = relationship(
        foreign_keys=[source_snapshot_id],
    )
    waste_analysis_result: Mapped[WasteAnalysisResult | None] = relationship(
        back_populates="analysis_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    waste_category_breakdowns: Mapped[list[WasteCategoryBreakdown]] = relationship(
        back_populates="analysis_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    waste_vendor_findings: Mapped[list[WasteVendorFinding]] = relationship(
        back_populates="analysis_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    simulation_run: Mapped[SimulationRun | None] = relationship(
        back_populates="analysis_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    reports: Mapped[list[Report]] = relationship(
        back_populates="analysis_run",
    )
    recommendations: Mapped[list[Recommendation]] = relationship(
        back_populates="analysis_run",
    )
    risk_analysis_result: Mapped[RiskAnalysisResult | None] = relationship(
        back_populates="analysis_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    risk_findings: Mapped[list[RiskFinding]] = relationship(
        back_populates="analysis_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
