"""AI-native simulation scenario contract (Sprint 5)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

ScenarioActionType = Literal[
    "reduce_expense",
    "increase_revenue",
    "reduce_budget",
    "increase_budget",
    "reduce_waste",
    "increase_profit",
    "reduce_suppliers",
    "close_branches",
    "hire_employees",
    "increase_payroll",
    "increase_prices",
    "reduce_transport",
    "investment",
    "operational_change",
    "mixed",
]

ValueMode = Literal["percent", "absolute", "count"]


class ScenarioAction(BaseModel):
    action_type: ScenarioActionType
    mode: ValueMode = "percent"
    value: float | None = None
    amount: float | None = None
    category: str | None = None
    department: str | None = None
    description: str = ""


class InterpretedScenario(BaseModel):
    scenario_type: str = Field(..., min_length=1, max_length=100)
    title_ar: str = Field(..., min_length=1, max_length=300)
    summary_ar: str = Field(..., min_length=1, max_length=1000)
    target_amount: float | None = None
    currency: str = "SAR"
    horizon_quarters: int = Field(default=4, ge=1, le=12)
    actions: list[ScenarioAction] = Field(..., min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    confidence: int = Field(default=75, ge=0, le=100)

    @field_validator("actions")
    @classmethod
    def _require_actions(cls, value: list[ScenarioAction]) -> list[ScenarioAction]:
        if not value:
            raise ValueError("At least one action is required")
        return value

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class MetricRangePayload(BaseModel):
    worst: float
    expected: float
    best: float
    label: str = ""


class FinancialRealityPayload(BaseModel):
    expense_baseline: float
    expense_projected: float
    expense_change: MetricRangePayload
    revenue_impact: MetricRangePayload | None = None
    cash_impact: MetricRangePayload
    confidence_level: str
    confidence_score: int = Field(ge=0, le=100)
    confidence_rationale: str
    action_reasonings: list[str] = Field(default_factory=list)
    validation_notes: list[str] = Field(default_factory=list)
    assumptions_used: list[str] = Field(default_factory=list)


class ExecutiveJudgmentPayload(BaseModel):
    """Senior financial consultant judgment — materiality, realism, verdict."""

    materiality_analysis: str
    financial_realism: str
    scale_comparison: str
    strategic_advice: str
    recommendation: str = Field(..., description="Arabic label: الموافقة / الموافقة مع تعديلات / التأجيل / الرفض")
    recommendation_type: Literal[
        "approve", "approve_with_modifications", "postpone", "reject"
    ]
    recommendation_rationale: str
    financial_reasoning: str
    supporting_indicators: list[str] = Field(default_factory=list)
    assumptions_used: list[str] = Field(default_factory=list)
    remaining_risks: str
    executive_verdict: str
    financial_justification: str
    strategic_recommendation: str
    confidence_statement: str
    alternative_option: str
    next_step: str


class SimulationExplanation(BaseModel):
    executive_summary: str
    expected_impact: str
    financial_changes: str
    risks: str
    benefits: str
    confidence: str
    assumptions: str
    board_recommendation: str
    next_actions: list[str] = Field(default_factory=list)
    forecast_ranges: str = ""
    executive_judgment: ExecutiveJudgmentPayload | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
