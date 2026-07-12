from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.db.models import (
    SimulationActionItem,
    SimulationAssumption,
    SimulationChartPoint,
    SimulationComparisonMetric,
    SimulationForecastSummary,
    SimulationImpactItem,
    SimulationRun,
    SimulationScenario,
)
from app.repositories.base import BaseRepository


class SimulationRepository(BaseRepository):
    """Data access for the Business Scenario Simulation domain
    (scenarios, assumptions, runs, and run result tables)."""

    # -- scenarios -----------------------------------------------------------

    def create_scenario(self, scenario: SimulationScenario) -> SimulationScenario:
        return self._add(scenario)

    def get_scenario(self, scenario_id: uuid.UUID) -> SimulationScenario | None:
        return self._get(SimulationScenario, scenario_id)

    def require_scenario(self, scenario_id: uuid.UUID) -> SimulationScenario:
        return self._require(SimulationScenario, scenario_id)

    def list_scenarios(
        self,
        organization_id: uuid.UUID,
        *,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SimulationScenario]:
        """Scenario catalog for the Simulation page (design §9)."""
        stmt = select(SimulationScenario).where(
            SimulationScenario.organization_id == organization_id
        )
        if status is not None:
            stmt = stmt.where(SimulationScenario.status == status)
        stmt = self._paginate(
            stmt.order_by(SimulationScenario.created_at), limit, offset
        )
        return self._list(stmt)

    def update_scenario(
        self, scenario: SimulationScenario, values: dict[str, Any]
    ) -> SimulationScenario:
        return self._update(scenario, values)

    def delete_scenario(self, scenario: SimulationScenario) -> None:
        """Deletes the scenario; assumptions cascade, runs RESTRICT at DB level."""
        self._delete(scenario)

    # -- assumptions -----------------------------------------------------------

    def add_assumptions(
        self, assumptions: list[SimulationAssumption]
    ) -> list[SimulationAssumption]:
        return self._add_all(assumptions)

    def list_assumptions(self, scenario_id: uuid.UUID) -> list[SimulationAssumption]:
        stmt = (
            select(SimulationAssumption)
            .where(SimulationAssumption.scenario_id == scenario_id)
            .order_by(SimulationAssumption.display_order)
        )
        return self._list(stmt)

    # -- runs -------------------------------------------------------------------

    def create_run(self, run: SimulationRun) -> SimulationRun:
        return self._add(run)

    def get_run(self, run_id: uuid.UUID) -> SimulationRun | None:
        return self._get(SimulationRun, run_id)

    def require_run(self, run_id: uuid.UUID) -> SimulationRun:
        return self._require(SimulationRun, run_id)

    def get_run_for_analysis_run(
        self, analysis_run_id: uuid.UUID
    ) -> SimulationRun | None:
        """1:1 lookup via the unique analysis_run_id FK."""
        stmt = select(SimulationRun).where(
            SimulationRun.analysis_run_id == analysis_run_id
        )
        return self._session.scalars(stmt).first()

    def list_runs_for_scenario(
        self,
        scenario_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SimulationRun]:
        stmt = self._paginate(
            select(SimulationRun)
            .where(SimulationRun.scenario_id == scenario_id)
            .order_by(SimulationRun.created_at.desc()),
            limit,
            offset,
        )
        return self._list(stmt)

    def update_run(self, run: SimulationRun, values: dict[str, Any]) -> SimulationRun:
        return self._update(run, values)

    # -- run results ---------------------------------------------------------------

    def set_forecast_summary(
        self, summary: SimulationForecastSummary
    ) -> SimulationForecastSummary:
        return self._add(summary)

    def get_forecast_summary(
        self, simulation_run_id: uuid.UUID
    ) -> SimulationForecastSummary | None:
        stmt = select(SimulationForecastSummary).where(
            SimulationForecastSummary.simulation_run_id == simulation_run_id
        )
        return self._session.scalars(stmt).first()

    def add_chart_points(
        self, points: list[SimulationChartPoint]
    ) -> list[SimulationChartPoint]:
        return self._add_all(points)

    def list_chart_points(
        self, simulation_run_id: uuid.UUID
    ) -> list[SimulationChartPoint]:
        stmt = (
            select(SimulationChartPoint)
            .where(SimulationChartPoint.simulation_run_id == simulation_run_id)
            .order_by(SimulationChartPoint.quarter_order)
        )
        return self._list(stmt)

    def add_comparison_metrics(
        self, metrics: list[SimulationComparisonMetric]
    ) -> list[SimulationComparisonMetric]:
        return self._add_all(metrics)

    def list_comparison_metrics(
        self, simulation_run_id: uuid.UUID
    ) -> list[SimulationComparisonMetric]:
        stmt = (
            select(SimulationComparisonMetric)
            .where(
                SimulationComparisonMetric.simulation_run_id == simulation_run_id
            )
            .order_by(SimulationComparisonMetric.display_order)
        )
        return self._list(stmt)

    def add_impact_items(
        self, items: list[SimulationImpactItem]
    ) -> list[SimulationImpactItem]:
        return self._add_all(items)

    def list_impact_items(
        self, simulation_run_id: uuid.UUID
    ) -> list[SimulationImpactItem]:
        stmt = (
            select(SimulationImpactItem)
            .where(SimulationImpactItem.simulation_run_id == simulation_run_id)
            .order_by(SimulationImpactItem.display_order)
        )
        return self._list(stmt)

    def add_action_items(
        self, items: list[SimulationActionItem]
    ) -> list[SimulationActionItem]:
        return self._add_all(items)

    def list_action_items(
        self, simulation_run_id: uuid.UUID
    ) -> list[SimulationActionItem]:
        stmt = (
            select(SimulationActionItem)
            .where(SimulationActionItem.simulation_run_id == simulation_run_id)
            .order_by(SimulationActionItem.created_at)
        )
        return self._list(stmt)

    def update_action_item(
        self, item: SimulationActionItem, values: dict[str, Any]
    ) -> SimulationActionItem:
        return self._update(item, values)
