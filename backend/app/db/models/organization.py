from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.analysis import AnalysisRun
    from app.db.models.department import Department
    from app.db.models.recommendation import Recommendation
    from app.db.models.repository import DataQualitySnapshot, FinancialFile
    from app.db.models.reporting import Report
    from app.db.models.risk import Risk
    from app.db.models.simulation import SimulationScenario
    from app.db.models.timeline import TimelineEvent
    from app.db.models.waste import WasteTrendPoint


class Organization(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform_name: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="خزينة"
    )
    executive_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )

    reporting_periods: Mapped[list[ReportingPeriod]] = relationship(
        back_populates="organization",
    )
    departments: Mapped[list[Department]] = relationship(
        back_populates="organization",
    )
    financial_files: Mapped[list[FinancialFile]] = relationship(
        back_populates="organization",
    )
    analysis_runs: Mapped[list[AnalysisRun]] = relationship(
        back_populates="organization",
    )
    risks: Mapped[list[Risk]] = relationship(
        back_populates="organization",
    )
    simulation_scenarios: Mapped[list[SimulationScenario]] = relationship(
        back_populates="organization",
    )
    reports: Mapped[list[Report]] = relationship(
        back_populates="organization",
    )
    recommendations: Mapped[list[Recommendation]] = relationship(
        back_populates="organization",
    )
    timeline_events: Mapped[list[TimelineEvent]] = relationship(
        back_populates="organization",
    )
    data_quality_snapshots: Mapped[list[DataQualitySnapshot]] = relationship(
        back_populates="organization",
    )
    waste_trend_points: Mapped[list[WasteTrendPoint]] = relationship(
        back_populates="organization",
    )


class ReportingPeriod(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "reporting_periods"
    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR start_date IS NULL OR end_date >= start_date",
            name="ck_reporting_periods_valid_date_range",
        ),
        Index(
            "uq_reporting_periods_one_active_per_org",
            "organization_id",
            unique=True,
            postgresql_where=text("is_active IS TRUE"),
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )

    organization: Mapped[Organization] = relationship(
        back_populates="reporting_periods",
    )
    financial_files: Mapped[list[FinancialFile]] = relationship(
        back_populates="reporting_period",
    )
    analysis_runs: Mapped[list[AnalysisRun]] = relationship(
        back_populates="reporting_period",
    )
    reports: Mapped[list[Report]] = relationship(
        back_populates="reporting_period",
    )
    risks: Mapped[list[Risk]] = relationship(
        back_populates="reporting_period",
    )
    timeline_events: Mapped[list[TimelineEvent]] = relationship(
        back_populates="reporting_period",
    )
    data_quality_snapshots: Mapped[list[DataQualitySnapshot]] = relationship(
        back_populates="reporting_period",
    )
    waste_trend_points: Mapped[list[WasteTrendPoint]] = relationship(
        back_populates="reporting_period",
    )
