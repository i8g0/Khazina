from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Numeric, SmallInteger, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.models.enums import SimulationActionStatus, SimulationScenarioStatus

if TYPE_CHECKING:
    from app.db.models.analysis import AnalysisRun
    from app.db.models.organization import Organization
    from app.db.models.recommendation import Recommendation


class SimulationScenario(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "simulation_scenarios"
    __table_args__ = (
        Index("ix_simulation_scenarios_org_status", "organization_id", "status"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=SimulationScenarioStatus.DRAFT.value,
    )

    organization: Mapped[Organization] = relationship(
        back_populates="simulation_scenarios",
    )
    assumptions: Mapped[list[SimulationAssumption]] = relationship(
        back_populates="scenario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    runs: Mapped[list[SimulationRun]] = relationship(
        back_populates="scenario",
    )


class SimulationAssumption(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulation_assumptions"

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    display_order: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )

    scenario: Mapped[SimulationScenario] = relationship(
        back_populates="assumptions",
    )


class SimulationRun(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulation_runs"
    __table_args__ = (
        UniqueConstraint("analysis_run_id", name="uq_simulation_runs_analysis_run_id"),
        Index("ix_simulation_runs_scenario_id", "scenario_id"),
    )

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_scenarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    result_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    result_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_label: Mapped[str | None] = mapped_column(String(20), nullable=True)

    scenario: Mapped[SimulationScenario] = relationship(
        back_populates="runs",
    )
    analysis_run: Mapped[AnalysisRun] = relationship(
        back_populates="simulation_run",
    )
    forecast_summary: Mapped[SimulationForecastSummary | None] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    chart_points: Mapped[list[SimulationChartPoint]] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comparison_metrics: Mapped[list[SimulationComparisonMetric]] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    impact_items: Mapped[list[SimulationImpactItem]] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    action_items: Mapped[list[SimulationActionItem]] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    recommendations: Mapped[list[Recommendation]] = relationship(
        back_populates="simulation_run",
    )


class SimulationForecastSummary(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulation_forecast_summaries"
    __table_args__ = (
        UniqueConstraint(
            "simulation_run_id",
            name="uq_simulation_forecast_summaries_simulation_run_id",
        ),
    )

    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    baseline_label: Mapped[str] = mapped_column(String(100), nullable=False)
    baseline_value: Mapped[str] = mapped_column(String(100), nullable=False)
    projected_label: Mapped[str] = mapped_column(String(100), nullable=False)
    projected_value: Mapped[str] = mapped_column(String(100), nullable=False)
    delta_label: Mapped[str] = mapped_column(String(100), nullable=False)
    delta_value: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence_label: Mapped[str | None] = mapped_column(String(20), nullable=True)

    simulation_run: Mapped[SimulationRun] = relationship(
        back_populates="forecast_summary",
    )


class SimulationChartPoint(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulation_chart_points"

    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    quarter_label: Mapped[str] = mapped_column(String(50), nullable=False)
    quarter_order: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    baseline_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    projected_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)

    simulation_run: Mapped[SimulationRun] = relationship(
        back_populates="chart_points",
    )


class SimulationComparisonMetric(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulation_comparison_metrics"

    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    metric_name: Mapped[str] = mapped_column(String(200), nullable=False)
    current_value: Mapped[str] = mapped_column(String(100), nullable=False)
    simulated_value: Mapped[str] = mapped_column(String(100), nullable=False)
    change_value: Mapped[str] = mapped_column(String(100), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    display_order: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )

    simulation_run: Mapped[SimulationRun] = relationship(
        back_populates="comparison_metrics",
    )


class SimulationImpactItem(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulation_impact_items"

    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_label: Mapped[str] = mapped_column(String(200), nullable=False)
    baseline_value: Mapped[str] = mapped_column(String(100), nullable=False)
    projected_value: Mapped[str] = mapped_column(String(100), nullable=False)
    change_value: Mapped[str] = mapped_column(String(100), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    display_order: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )

    simulation_run: Mapped[SimulationRun] = relationship(
        back_populates="impact_items",
    )


class SimulationActionItem(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulation_action_items"

    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=SimulationActionStatus.PROPOSED.value,
    )

    simulation_run: Mapped[SimulationRun] = relationship(
        back_populates="action_items",
    )
