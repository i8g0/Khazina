"""Universal AI-native scenario calculator — delegates to FinancialRealityEngine (Sprint 6)."""

from __future__ import annotations

from dataclasses import dataclass

from app.business.engines.scenario.calculator import ScenarioCalculationResult
from app.business.engines.scenario.financial_reality import (
    FinancialRealityEngine,
    RealisticFinancialOutcome,
)
from app.business.engines.scenario.input import ScenarioBaselineInput
from app.scenario.ai_contract import InterpretedScenario


@dataclass
class UniversalScenarioInput:
    interpreted: InterpretedScenario
    baseline: ScenarioBaselineInput
    user_request: str


@dataclass(frozen=True, slots=True)
class UniversalScenarioResult:
    calculation: ScenarioCalculationResult
    financial_reality: RealisticFinancialOutcome


class UniversalScenarioCalculator:
    """Applies AI-interpreted actions via CFO-grade financial constraints."""

    def __init__(self, *, engine: FinancialRealityEngine | None = None) -> None:
        self._engine = engine or FinancialRealityEngine()

    def calculate(self, input_data: UniversalScenarioInput) -> UniversalScenarioResult:
        calculation, financial = self._engine.simulate(
            input_data.interpreted,
            input_data.baseline,
        )
        return UniversalScenarioResult(calculation=calculation, financial_reality=financial)
