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

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
