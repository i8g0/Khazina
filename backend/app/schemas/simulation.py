"""Simulation API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.schemas.common import FullTimestampResponse, SchemaBase, TimestampResponse


class SimulationAssumptionInput(SchemaBase):
    label: str = Field(..., min_length=1, max_length=200)
    value: str = Field(..., min_length=1, max_length=500)
    display_order: int = Field(0, ge=0)


class SimulationScenarioCreate(SchemaBase):
    name: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    assumptions: list[SimulationAssumptionInput] = Field(..., min_length=1)


class SimulationScenarioUpdate(SchemaBase):
    name: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = Field(None, min_length=1)


class SimulationScenarioResponse(FullTimestampResponse):
    id: UUID
    organization_id: UUID
    name: str
    description: str
    status: str


class SimulationAssumptionResponse(TimestampResponse):
    id: UUID
    scenario_id: UUID
    label: str
    value: str
    display_order: int


class SimulationRunRequest(SchemaBase):
    reporting_period_id: UUID | None = None


class SimulationRunResponse(TimestampResponse):
    id: UUID
    scenario_id: UUID
    analysis_run_id: UUID
    result_title: str | None
    result_description: str | None
    confidence_label: str | None


class SimulationForecastSummaryInput(SchemaBase):
    baseline_label: str = Field(..., min_length=1, max_length=100)
    baseline_value: str = Field(..., min_length=1, max_length=100)
    projected_label: str = Field(..., min_length=1, max_length=100)
    projected_value: str = Field(..., min_length=1, max_length=100)
    delta_label: str = Field(..., min_length=1, max_length=100)
    delta_value: str = Field(..., min_length=1, max_length=100)
    confidence_label: str | None = Field(None, max_length=20)


class SimulationChartPointInput(SchemaBase):
    quarter_label: str = Field(..., min_length=1, max_length=50)
    quarter_order: int = Field(..., ge=0)
    baseline_amount: float
    projected_amount: float


class SimulationComparisonMetricInput(SchemaBase):
    metric_name: str = Field(..., min_length=1, max_length=200)
    current_value: str = Field(..., max_length=100)
    simulated_value: str = Field(..., max_length=100)
    change_value: str = Field(..., max_length=100)
    direction: str = Field(..., max_length=20)
    display_order: int = Field(0, ge=0)


class SimulationImpactItemInput(SchemaBase):
    category_label: str = Field(..., min_length=1, max_length=200)
    baseline_value: str = Field(..., max_length=100)
    projected_value: str = Field(..., max_length=100)
    change_value: str = Field(..., max_length=100)
    direction: str = Field(..., max_length=20)
    display_order: int = Field(0, ge=0)


class SimulationActionItemInput(SchemaBase):
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)


class SimulationRunResultsCreate(SchemaBase):
    result_title: str | None = Field(None, max_length=300)
    result_description: str | None = None
    confidence_label: str | None = Field(None, max_length=20)
    forecast_summary: SimulationForecastSummaryInput | None = None
    chart_points: list[SimulationChartPointInput] | None = None
    comparison_metrics: list[SimulationComparisonMetricInput] | None = None
    impact_items: list[SimulationImpactItemInput] | None = None
    action_items: list[SimulationActionItemInput] | None = None


class SimulationForecastSummaryResponse(TimestampResponse):
    id: UUID
    simulation_run_id: UUID
    baseline_label: str
    baseline_value: str
    projected_label: str
    projected_value: str
    delta_label: str
    delta_value: str
    confidence_label: str | None


class SimulationChartPointResponse(TimestampResponse):
    id: UUID
    simulation_run_id: UUID
    quarter_label: str
    quarter_order: int
    baseline_amount: float
    projected_amount: float


class SimulationComparisonMetricResponse(TimestampResponse):
    id: UUID
    simulation_run_id: UUID
    metric_name: str
    current_value: str
    simulated_value: str
    change_value: str
    direction: str
    display_order: int


class SimulationImpactItemResponse(TimestampResponse):
    id: UUID
    simulation_run_id: UUID
    category_label: str
    baseline_value: str
    projected_value: str
    change_value: str
    direction: str
    display_order: int


class SimulationActionItemResponse(TimestampResponse):
    id: UUID
    simulation_run_id: UUID
    title: str
    description: str
    status: str
