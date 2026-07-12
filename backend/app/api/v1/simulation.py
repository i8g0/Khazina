"""Simulation REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import PaginationDep, SimulationServiceDep
from app.schemas.response import ApiResponse, success_response
from app.schemas.simulation import (
    SimulationActionItemResponse,
    SimulationAssumptionResponse,
    SimulationChartPointResponse,
    SimulationComparisonMetricResponse,
    SimulationForecastSummaryResponse,
    SimulationImpactItemResponse,
    SimulationRunRequest,
    SimulationRunResponse,
    SimulationRunResultsCreate,
    SimulationScenarioCreate,
    SimulationScenarioResponse,
    SimulationScenarioUpdate,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/simulation",
    tags=["simulation"],
)


@router.post(
    "/scenarios",
    response_model=ApiResponse[SimulationScenarioResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create simulation scenario",
)
def create_scenario(
    organization_id: UUID,
    body: SimulationScenarioCreate,
    service: SimulationServiceDep,
) -> ApiResponse[SimulationScenarioResponse]:
    assumptions = (
        [a.model_dump() for a in body.assumptions] if body.assumptions else None
    )
    scenario = service.create_scenario(
        organization_id,
        name=body.name,
        description=body.description,
        assumptions=assumptions,
    )
    return success_response(
        data=SimulationScenarioResponse.model_validate(scenario),
        message="Scenario created",
    )


@router.get(
    "/scenarios",
    response_model=ApiResponse[list[SimulationScenarioResponse]],
    summary="List simulation scenarios",
)
def list_scenarios(
    organization_id: UUID,
    service: SimulationServiceDep,
    pagination: PaginationDep,
    status_filter: str | None = Query(None, alias="status"),
) -> ApiResponse[list[SimulationScenarioResponse]]:
    scenarios = service.list_scenarios(
        organization_id,
        status=status_filter,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[SimulationScenarioResponse.model_validate(s) for s in scenarios],
        message="Scenarios retrieved",
    )


@router.get(
    "/scenarios/{scenario_id}",
    response_model=ApiResponse[SimulationScenarioResponse],
    summary="Get simulation scenario by ID",
)
def get_scenario(
    organization_id: UUID,
    scenario_id: UUID,
    service: SimulationServiceDep,
) -> ApiResponse[SimulationScenarioResponse]:
    scenario = service.get_scenario(scenario_id)
    return success_response(
        data=SimulationScenarioResponse.model_validate(scenario),
        message="Scenario retrieved",
    )


@router.patch(
    "/scenarios/{scenario_id}",
    response_model=ApiResponse[SimulationScenarioResponse],
    summary="Update draft simulation scenario",
)
def update_scenario(
    organization_id: UUID,
    scenario_id: UUID,
    body: SimulationScenarioUpdate,
    service: SimulationServiceDep,
) -> ApiResponse[SimulationScenarioResponse]:
    scenario = service.update_scenario(
        organization_id, scenario_id, name=body.name, description=body.description
    )
    return success_response(
        data=SimulationScenarioResponse.model_validate(scenario),
        message="Scenario updated",
    )


@router.delete(
    "/scenarios/{scenario_id}",
    response_model=ApiResponse[None],
    summary="Delete simulation scenario",
)
def delete_scenario(
    organization_id: UUID,
    scenario_id: UUID,
    service: SimulationServiceDep,
) -> ApiResponse[None]:
    service.delete_scenario(organization_id, scenario_id)
    return success_response(data=None, message="Scenario deleted")


@router.get(
    "/scenarios/{scenario_id}/assumptions",
    response_model=ApiResponse[list[SimulationAssumptionResponse]],
    summary="List scenario assumptions",
)
def list_assumptions(
    organization_id: UUID,
    scenario_id: UUID,
    service: SimulationServiceDep,
) -> ApiResponse[list[SimulationAssumptionResponse]]:
    assumptions = service.list_assumptions(organization_id, scenario_id)
    return success_response(
        data=[SimulationAssumptionResponse.model_validate(a) for a in assumptions],
        message="Assumptions retrieved",
    )


@router.post(
    "/scenarios/{scenario_id}/run",
    response_model=ApiResponse[SimulationRunResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Run simulation scenario",
)
def run_scenario(
    organization_id: UUID,
    scenario_id: UUID,
    body: SimulationRunRequest,
    service: SimulationServiceDep,
) -> ApiResponse[SimulationRunResponse]:
    run = service.run_scenario(
        organization_id,
        scenario_id,
        reporting_period_id=body.reporting_period_id,
    )
    return success_response(
        data=SimulationRunResponse.model_validate(run),
        message="Simulation run started",
    )


@router.get(
    "/scenarios/{scenario_id}/runs",
    response_model=ApiResponse[list[SimulationRunResponse]],
    summary="List runs for a scenario",
)
def list_runs_for_scenario(
    organization_id: UUID,
    scenario_id: UUID,
    service: SimulationServiceDep,
    pagination: PaginationDep,
) -> ApiResponse[list[SimulationRunResponse]]:
    runs = service.list_runs_for_scenario(
        organization_id,
        scenario_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[SimulationRunResponse.model_validate(r) for r in runs],
        message="Simulation runs retrieved",
    )


@router.get(
    "/runs/{run_id}",
    response_model=ApiResponse[SimulationRunResponse],
    summary="Get simulation run by ID",
)
def get_simulation_run(
    organization_id: UUID,
    run_id: UUID,
    service: SimulationServiceDep,
) -> ApiResponse[SimulationRunResponse]:
    run = service.get_run(run_id)
    return success_response(
        data=SimulationRunResponse.model_validate(run),
        message="Simulation run retrieved",
    )


@router.post(
    "/runs/{run_id}/results",
    response_model=ApiResponse[SimulationRunResponse],
    summary="Record simulation run results",
)
def record_run_results(
    organization_id: UUID,
    run_id: UUID,
    body: SimulationRunResultsCreate,
    service: SimulationServiceDep,
) -> ApiResponse[SimulationRunResponse]:
    run = service.record_run_results(
        organization_id,
        run_id,
        result_title=body.result_title,
        result_description=body.result_description,
        confidence_label=body.confidence_label,
        forecast_summary=(
            body.forecast_summary.model_dump() if body.forecast_summary else None
        ),
        chart_points=(
            [p.model_dump() for p in body.chart_points] if body.chart_points else None
        ),
        comparison_metrics=(
            [m.model_dump() for m in body.comparison_metrics]
            if body.comparison_metrics
            else None
        ),
        impact_items=(
            [i.model_dump() for i in body.impact_items] if body.impact_items else None
        ),
        action_items=(
            [a.model_dump() for a in body.action_items] if body.action_items else None
        ),
    )
    return success_response(
        data=SimulationRunResponse.model_validate(run),
        message="Simulation results recorded",
    )


@router.get(
    "/runs/{run_id}/forecast-summary",
    response_model=ApiResponse[SimulationForecastSummaryResponse | None],
    summary="Get simulation forecast summary",
)
def get_forecast_summary(
    organization_id: UUID,
    run_id: UUID,
    service: SimulationServiceDep,
) -> ApiResponse[SimulationForecastSummaryResponse | None]:
    summary = service.get_forecast_summary(organization_id, run_id)
    data = (
        SimulationForecastSummaryResponse.model_validate(summary)
        if summary
        else None
    )
    return success_response(data=data, message="Forecast summary retrieved")


@router.get(
    "/runs/{run_id}/chart-points",
    response_model=ApiResponse[list[SimulationChartPointResponse]],
    summary="List simulation chart points",
)
def list_chart_points(
    organization_id: UUID,
    run_id: UUID,
    service: SimulationServiceDep,
) -> ApiResponse[list[SimulationChartPointResponse]]:
    points = service.list_chart_points(organization_id, run_id)
    return success_response(
        data=[SimulationChartPointResponse.model_validate(p) for p in points],
        message="Chart points retrieved",
    )


@router.get(
    "/runs/{run_id}/comparison-metrics",
    response_model=ApiResponse[list[SimulationComparisonMetricResponse]],
    summary="List simulation comparison metrics",
)
def list_comparison_metrics(
    organization_id: UUID,
    run_id: UUID,
    service: SimulationServiceDep,
) -> ApiResponse[list[SimulationComparisonMetricResponse]]:
    metrics = service.list_comparison_metrics(organization_id, run_id)
    return success_response(
        data=[SimulationComparisonMetricResponse.model_validate(m) for m in metrics],
        message="Comparison metrics retrieved",
    )


@router.get(
    "/runs/{run_id}/impact-items",
    response_model=ApiResponse[list[SimulationImpactItemResponse]],
    summary="List simulation impact items",
)
def list_impact_items(
    organization_id: UUID,
    run_id: UUID,
    service: SimulationServiceDep,
) -> ApiResponse[list[SimulationImpactItemResponse]]:
    items = service.list_impact_items(organization_id, run_id)
    return success_response(
        data=[SimulationImpactItemResponse.model_validate(i) for i in items],
        message="Impact items retrieved",
    )


@router.get(
    "/runs/{run_id}/action-items",
    response_model=ApiResponse[list[SimulationActionItemResponse]],
    summary="List simulation action items",
)
def list_action_items(
    organization_id: UUID,
    run_id: UUID,
    service: SimulationServiceDep,
) -> ApiResponse[list[SimulationActionItemResponse]]:
    items = service.list_action_items(organization_id, run_id)
    return success_response(
        data=[SimulationActionItemResponse.model_validate(i) for i in items],
        message="Action items retrieved",
    )
