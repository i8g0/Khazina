"""Business Scenario Simulation services: scenario workflow and run results."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    AnalysisRun,
    SimulationActionItem,
    SimulationAssumption,
    SimulationChartPoint,
    SimulationComparisonMetric,
    SimulationForecastSummary,
    SimulationImpactItem,
    SimulationRun,
    SimulationScenario,
)
from app.db.models.enums import (
    AnalysisRunStatus,
    AnalysisType,
    MetricDirection,
    SimulationScenarioStatus,
)
from app.repositories import (
    AnalysisRepository,
    OrganizationRepository,
    SimulationRepository,
)
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    DuplicateResourceError,
    InvalidStateError,
    ResourceNotFoundError,
)


class SimulationService(BaseService):
    """Business use cases for the simulation workflow.

    Scenarios are authored in ``draft`` and become ``completed`` once a run
    finishes. Executing a scenario creates the shared ``AnalysisRun`` parent
    (type ``simulation``) and its 1:1 ``SimulationRun`` in one transaction.
    Forecast computation is out of scope; this service persists and
    validates results the engine will produce.
    """

    def __init__(
        self,
        session: Session,
        simulation_repository: SimulationRepository,
        analysis_repository: AnalysisRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        super().__init__(session)
        self._simulations = simulation_repository
        self._analyses = analysis_repository
        self._organizations = organization_repository

    # -- scenario authoring ------------------------------------------------------

    def create_scenario(
        self,
        organization_id: uuid.UUID,
        *,
        name: str,
        description: str,
        assumptions: list[dict[str, Any]] | None = None,
    ) -> SimulationScenario:
        self._require_organization(organization_id)
        name = name.strip()
        description = description.strip()
        if not name or not description:
            raise BusinessValidationError(
                "Scenario name and description must not be empty"
            )

        assumption_rows = self._build_assumptions(assumptions or [])
        scenario = SimulationScenario(
            organization_id=organization_id,
            name=name,
            description=description,
            status=SimulationScenarioStatus.DRAFT,
        )
        with self._transaction():
            self._simulations.create_scenario(scenario)
            for row in assumption_rows:
                row.scenario_id = scenario.id
            if assumption_rows:
                self._simulations.add_assumptions(assumption_rows)
        return scenario

    def get_scenario(self, scenario_id: uuid.UUID) -> SimulationScenario:
        return self._found(
            self._simulations.get_scenario(scenario_id),
            "SimulationScenario",
            scenario_id,
        )

    def list_scenarios(
        self,
        organization_id: uuid.UUID,
        *,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SimulationScenario]:
        self._require_organization(organization_id)
        return self._simulations.list_scenarios(
            organization_id, status=status, limit=limit, offset=offset
        )

    def list_assumptions(
        self, organization_id: uuid.UUID, scenario_id: uuid.UUID
    ) -> list[SimulationAssumption]:
        self._owned_scenario(organization_id, scenario_id)
        return self._simulations.list_assumptions(scenario_id)

    def update_scenario(
        self,
        organization_id: uuid.UUID,
        scenario_id: uuid.UUID,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> SimulationScenario:
        scenario = self._owned_scenario(organization_id, scenario_id)
        if scenario.status != SimulationScenarioStatus.DRAFT:
            raise InvalidStateError("Only draft scenarios can be edited")

        values: dict[str, object] = {}
        if name is not None:
            name = name.strip()
            if not name:
                raise BusinessValidationError("Scenario name must not be empty")
            values["name"] = name
        if description is not None:
            description = description.strip()
            if not description:
                raise BusinessValidationError(
                    "Scenario description must not be empty"
                )
            values["description"] = description
        if not values:
            return scenario

        with self._transaction():
            self._simulations.update_scenario(scenario, values)
        return scenario

    def delete_scenario(
        self, organization_id: uuid.UUID, scenario_id: uuid.UUID
    ) -> None:
        """Deletes a draft scenario; scenarios with runs are protected (FK RESTRICT)."""
        scenario = self._owned_scenario(organization_id, scenario_id)
        if self._simulations.list_runs_for_scenario(scenario_id, limit=1):
            raise InvalidStateError(
                "A scenario with recorded runs cannot be deleted"
            )
        with self._transaction():
            self._simulations.delete_scenario(scenario)

    # -- execution workflow ----------------------------------------------------------

    def run_scenario(
        self,
        organization_id: uuid.UUID,
        scenario_id: uuid.UUID,
        *,
        reporting_period_id: uuid.UUID | None = None,
    ) -> SimulationRun:
        """Starts a simulation: shared analysis run + 1:1 simulation run."""
        scenario = self._owned_scenario(organization_id, scenario_id)
        if reporting_period_id is not None:
            period = self._organizations.get_reporting_period(reporting_period_id)
            if period is None:
                raise ResourceNotFoundError("ReportingPeriod", reporting_period_id)
            self._check_ownership(period, "ReportingPeriod", organization_id)

        analysis_run = AnalysisRun(
            organization_id=organization_id,
            reporting_period_id=reporting_period_id,
            analysis_type=AnalysisType.SIMULATION,
            title=scenario.name,
            status=AnalysisRunStatus.PROCESSING,
            started_at=datetime.now(timezone.utc),
        )
        with self._transaction():
            self._analyses.create(analysis_run)
            simulation_run = self._simulations.create_run(
                SimulationRun(
                    scenario_id=scenario.id,
                    analysis_run_id=analysis_run.id,
                )
            )
        return simulation_run

    def record_run_results(
        self,
        organization_id: uuid.UUID,
        simulation_run_id: uuid.UUID,
        *,
        result_title: str | None = None,
        result_description: str | None = None,
        confidence_label: str | None = None,
        forecast_summary: dict[str, Any] | None = None,
        chart_points: list[dict[str, Any]] | None = None,
        comparison_metrics: list[dict[str, Any]] | None = None,
        impact_items: list[dict[str, Any]] | None = None,
        action_items: list[dict[str, Any]] | None = None,
    ) -> SimulationRun:
        """Persists run results, completes the analysis run, finalizes the scenario."""
        run = self._owned_run(organization_id, simulation_run_id)
        analysis_run = self._analyses.get(run.analysis_run_id)
        if analysis_run is None:
            raise ResourceNotFoundError("AnalysisRun", run.analysis_run_id)
        if analysis_run.status != AnalysisRunStatus.PROCESSING:
            raise InvalidStateError(
                "Results can only be recorded for a processing simulation "
                f"(current status: '{analysis_run.status}')"
            )
        if self._simulations.get_forecast_summary(run.id) is not None:
            raise DuplicateResourceError(
                f"Simulation run '{run.id}' already has recorded results"
            )

        summary_row = (
            self._build_forecast_summary(run.id, forecast_summary)
            if forecast_summary is not None
            else None
        )
        point_rows = self._build_chart_points(run.id, chart_points or [])
        metric_rows = self._build_comparison_metrics(run.id, comparison_metrics or [])
        impact_rows = self._build_impact_items(run.id, impact_items or [])
        action_rows = self._build_action_items(run.id, action_items or [])
        scenario = self._simulations.get_scenario(run.scenario_id)

        with self._transaction():
            self._simulations.update_run(
                run,
                {
                    "result_title": result_title,
                    "result_description": result_description,
                    "confidence_label": confidence_label,
                },
            )
            if summary_row is not None:
                self._simulations.set_forecast_summary(summary_row)
            if point_rows:
                self._simulations.add_chart_points(point_rows)
            if metric_rows:
                self._simulations.add_comparison_metrics(metric_rows)
            if impact_rows:
                self._simulations.add_impact_items(impact_rows)
            if action_rows:
                self._simulations.add_action_items(action_rows)
            self._analyses.update(
                analysis_run,
                {
                    "status": AnalysisRunStatus.COMPLETED,
                    "completed_at": datetime.now(timezone.utc),
                },
            )
            if scenario is not None and scenario.status != (
                SimulationScenarioStatus.COMPLETED
            ):
                self._simulations.update_scenario(
                    scenario, {"status": SimulationScenarioStatus.COMPLETED}
                )
        return run

    # -- run retrieval -----------------------------------------------------------------

    def get_run(self, run_id: uuid.UUID) -> SimulationRun:
        return self._found(
            self._simulations.get_run(run_id), "SimulationRun", run_id
        )

    def list_runs_for_scenario(
        self,
        organization_id: uuid.UUID,
        scenario_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SimulationRun]:
        self._owned_scenario(organization_id, scenario_id)
        return self._simulations.list_runs_for_scenario(
            scenario_id, limit=limit, offset=offset
        )

    def get_forecast_summary(
        self, organization_id: uuid.UUID, simulation_run_id: uuid.UUID
    ) -> SimulationForecastSummary | None:
        run = self._owned_run(organization_id, simulation_run_id)
        return self._simulations.get_forecast_summary(run.id)

    def list_chart_points(
        self, organization_id: uuid.UUID, simulation_run_id: uuid.UUID
    ) -> list[SimulationChartPoint]:
        run = self._owned_run(organization_id, simulation_run_id)
        return self._simulations.list_chart_points(run.id)

    def list_comparison_metrics(
        self, organization_id: uuid.UUID, simulation_run_id: uuid.UUID
    ) -> list[SimulationComparisonMetric]:
        run = self._owned_run(organization_id, simulation_run_id)
        return self._simulations.list_comparison_metrics(run.id)

    def list_impact_items(
        self, organization_id: uuid.UUID, simulation_run_id: uuid.UUID
    ) -> list[SimulationImpactItem]:
        run = self._owned_run(organization_id, simulation_run_id)
        return self._simulations.list_impact_items(run.id)

    def list_action_items(
        self, organization_id: uuid.UUID, simulation_run_id: uuid.UUID
    ) -> list[SimulationActionItem]:
        run = self._owned_run(organization_id, simulation_run_id)
        return self._simulations.list_action_items(run.id)

    # -- internals ---------------------------------------------------------------------

    def _owned_scenario(
        self, organization_id: uuid.UUID, scenario_id: uuid.UUID
    ) -> SimulationScenario:
        scenario = self.get_scenario(scenario_id)
        self._check_ownership(scenario, "SimulationScenario", organization_id)
        return scenario

    def _owned_run(
        self, organization_id: uuid.UUID, run_id: uuid.UUID
    ) -> SimulationRun:
        """Ownership is derived from the run's parent scenario."""
        run = self.get_run(run_id)
        scenario = self._simulations.get_scenario(run.scenario_id)
        if scenario is None:
            raise ResourceNotFoundError("SimulationScenario", run.scenario_id)
        self._check_ownership(scenario, "SimulationScenario", organization_id)
        return run

    @staticmethod
    def _build_assumptions(
        assumptions: list[dict[str, Any]],
    ) -> list[SimulationAssumption]:
        rows: list[SimulationAssumption] = []
        for order, item in enumerate(assumptions):
            label = str(item.get("label", "")).strip()
            value = str(item.get("value", "")).strip()
            if not label or not value:
                raise BusinessValidationError(
                    "Each assumption requires a label and a value"
                )
            rows.append(
                SimulationAssumption(
                    label=label,
                    value=value,
                    display_order=item.get("display_order", order),
                )
            )
        return rows

    @staticmethod
    def _build_forecast_summary(
        run_id: uuid.UUID, summary: dict[str, Any]
    ) -> SimulationForecastSummary:
        required = (
            "baseline_label",
            "baseline_value",
            "projected_label",
            "projected_value",
            "delta_label",
            "delta_value",
        )
        missing = [field for field in required if not str(summary.get(field, "")).strip()]
        if missing:
            raise BusinessValidationError(
                f"Forecast summary is missing required fields: {', '.join(missing)}"
            )
        return SimulationForecastSummary(
            simulation_run_id=run_id,
            baseline_label=summary["baseline_label"],
            baseline_value=summary["baseline_value"],
            projected_label=summary["projected_label"],
            projected_value=summary["projected_value"],
            delta_label=summary["delta_label"],
            delta_value=summary["delta_value"],
            confidence_label=summary.get("confidence_label"),
        )

    @staticmethod
    def _build_chart_points(
        run_id: uuid.UUID, points: list[dict[str, Any]]
    ) -> list[SimulationChartPoint]:
        rows: list[SimulationChartPoint] = []
        for item in points:
            quarter_label = str(item.get("quarter_label", "")).strip()
            if not quarter_label:
                raise BusinessValidationError(
                    "Each chart point requires a quarter_label"
                )
            if item.get("quarter_order") is None:
                raise BusinessValidationError(
                    "Each chart point requires a quarter_order"
                )
            if item.get("baseline_amount") is None or item.get("projected_amount") is None:
                raise BusinessValidationError(
                    "Each chart point requires baseline_amount and projected_amount"
                )
            rows.append(
                SimulationChartPoint(
                    simulation_run_id=run_id,
                    quarter_label=quarter_label,
                    quarter_order=item["quarter_order"],
                    baseline_amount=item["baseline_amount"],
                    projected_amount=item["projected_amount"],
                )
            )
        return rows

    @staticmethod
    def _build_comparison_metrics(
        run_id: uuid.UUID, metrics: list[dict[str, Any]]
    ) -> list[SimulationComparisonMetric]:
        rows: list[SimulationComparisonMetric] = []
        for order, item in enumerate(metrics):
            metric_name = str(item.get("metric_name", "")).strip()
            direction = str(item.get("direction", "")).strip()
            if not metric_name:
                raise BusinessValidationError(
                    "Each comparison metric requires a metric_name"
                )
            if direction not in set(MetricDirection):
                raise BusinessValidationError(
                    f"Unknown metric direction '{direction}'"
                )
            rows.append(
                SimulationComparisonMetric(
                    simulation_run_id=run_id,
                    metric_name=metric_name,
                    current_value=item.get("current_value", ""),
                    simulated_value=item.get("simulated_value", ""),
                    change_value=item.get("change_value", ""),
                    direction=direction,
                    display_order=item.get("display_order", order),
                )
            )
        return rows

    @staticmethod
    def _build_impact_items(
        run_id: uuid.UUID, items: list[dict[str, Any]]
    ) -> list[SimulationImpactItem]:
        rows: list[SimulationImpactItem] = []
        for order, item in enumerate(items):
            category_label = str(item.get("category_label", "")).strip()
            direction = str(item.get("direction", "")).strip()
            if not category_label:
                raise BusinessValidationError(
                    "Each impact item requires a category_label"
                )
            if direction not in set(MetricDirection):
                raise BusinessValidationError(
                    f"Unknown impact direction '{direction}'"
                )
            rows.append(
                SimulationImpactItem(
                    simulation_run_id=run_id,
                    category_label=category_label,
                    baseline_value=item.get("baseline_value", ""),
                    projected_value=item.get("projected_value", ""),
                    change_value=item.get("change_value", ""),
                    direction=direction,
                    display_order=item.get("display_order", order),
                )
            )
        return rows

    @staticmethod
    def _build_action_items(
        run_id: uuid.UUID, items: list[dict[str, Any]]
    ) -> list[SimulationActionItem]:
        rows: list[SimulationActionItem] = []
        for item in items:
            title = str(item.get("title", "")).strip()
            description = str(item.get("description", "")).strip()
            if not title or not description:
                raise BusinessValidationError(
                    "Each action item requires a title and a description"
                )
            rows.append(
                SimulationActionItem(
                    simulation_run_id=run_id,
                    title=title,
                    description=description,
                )
            )
        return rows

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
