from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.analysis import AnalysisRun
    from app.db.models.department import Department
    from app.db.models.organization import Organization, ReportingPeriod


class WasteAnalysisResult(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "waste_analysis_results"
    __table_args__ = (
        UniqueConstraint("analysis_run_id", name="uq_waste_analysis_results_analysis_run_id"),
        CheckConstraint(
            "waste_percentage >= 0 AND waste_percentage <= 100",
            name="ck_waste_analysis_results_waste_percentage_range",
        ),
    )

    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    total_waste_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    waste_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    top_category_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    top_category_percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    potential_savings_amount: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    active_savings_opportunities: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )

    analysis_run: Mapped[AnalysisRun] = relationship(
        back_populates="waste_analysis_result",
    )


class WasteCategoryBreakdown(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "waste_category_breakdowns"
    __table_args__ = (
        Index(
            "ix_waste_category_breakdowns_run_department",
            "analysis_run_id",
            "department_id",
        ),
    )

    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    category_name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    display_order: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )

    analysis_run: Mapped[AnalysisRun] = relationship(
        back_populates="waste_category_breakdowns",
    )
    department: Mapped[Department | None] = relationship(
        back_populates="waste_category_breakdowns",
    )


class WasteVendorFinding(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "waste_vendor_findings"

    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    vendor_name: Mapped[str] = mapped_column(String(300), nullable=False)
    category_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    deviation_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    analysis_run: Mapped[AnalysisRun] = relationship(
        back_populates="waste_vendor_findings",
    )


class WasteTrendPoint(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "waste_trend_points"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "reporting_period_id",
            "month_label",
            name="uq_waste_trend_points_org_period_month",
        ),
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
    month_label: Mapped[str] = mapped_column(String(50), nullable=False)
    month_order: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    waste_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)

    organization: Mapped[Organization] = relationship(
        back_populates="waste_trend_points",
    )
    reporting_period: Mapped[ReportingPeriod | None] = relationship(
        back_populates="waste_trend_points",
    )
