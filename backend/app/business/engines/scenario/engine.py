"""Business Scenario Engine (Sprint 6.5)."""

from __future__ import annotations

from typing import Any

from app.business.assemblers.scenario import ScenarioFactAssembler
from app.business.base import BusinessEngine
from app.business.engines.scenario.calculator import (
    ScenarioCalculationResult,
    ScenarioCalculator,
)
from app.business.engines.scenario.detector import ScenarioDetectionResult, ScenarioDetector
from app.business.engines.scenario.input import (
    ScenarioArchetype,
    ScenarioBaselineInput,
    ScenarioEngineInput,
)
from app.business.engines.scenario.manifest import SCENARIO_ENGINE_MANIFEST
from app.business.exceptions import InvalidInputError, ValidationError
from app.business.facts.contract import FactsContract
from app.business.manifest import EngineManifest


class ScenarioEngine(BusinessEngine):
    """Coordinates validation, calculation, detection, and fact assembly."""

    def __init__(
        self,
        *,
        calculator: ScenarioCalculator | None = None,
        detector: ScenarioDetector | None = None,
        assembler: ScenarioFactAssembler | None = None,
    ) -> None:
        self._calculator = calculator or ScenarioCalculator()
        self._detector = detector or ScenarioDetector()
        self._assembler = assembler or ScenarioFactAssembler()

    @property
    def manifest(self) -> EngineManifest:
        return SCENARIO_ENGINE_MANIFEST

    def run(self, input_data: Any) -> FactsContract:
        validated = self._validate_input(input_data)
        calculation = self._calculator.calculate(validated)
        detection = self._detector.detect(calculation)
        return self.assemble_facts(calculation, detection)

    def assemble_facts(
        self,
        calculation_result: Any,
        detection_result: Any,
    ) -> FactsContract:
        if not isinstance(calculation_result, ScenarioCalculationResult):
            raise InvalidInputError(
                "calculation_result must be ScenarioCalculationResult"
            )
        if not isinstance(detection_result, ScenarioDetectionResult):
            raise InvalidInputError("detection_result must be ScenarioDetectionResult")
        return self._assembler.assemble(calculation_result, detection_result)

    def _validate_input(self, input_data: Any) -> ScenarioEngineInput:
        if not isinstance(input_data, ScenarioEngineInput):
            raise InvalidInputError("input_data must be ScenarioEngineInput")
        baseline = input_data.baseline
        if not isinstance(baseline, ScenarioBaselineInput):
            raise InvalidInputError("baseline must be ScenarioBaselineInput")
        if baseline.total_baseline <= 0:
            raise ValidationError("baseline.total_baseline must be greater than zero")
        if input_data.horizon_quarters < 1 or input_data.horizon_quarters > 12:
            raise ValidationError("horizon_quarters must be between 1 and 12")

        if input_data.archetype == ScenarioArchetype.SPENDING_REDUCTION:
            if input_data.reduction_percent is None:
                raise ValidationError("reduction_percent is required")
        elif input_data.archetype == ScenarioArchetype.SUPPLIER_CONSOLIDATION:
            if (
                input_data.suppliers_before is None
                or input_data.suppliers_after is None
                or input_data.admin_savings_rate is None
            ):
                raise ValidationError(
                    "suppliers_before, suppliers_after, and admin_savings_rate "
                    "are required"
                )
        elif input_data.archetype == ScenarioArchetype.MARKET_EXPANSION:
            if (
                input_data.revenue_growth_percent is None
                or input_data.expansion_cost is None
            ):
                raise ValidationError(
                    "revenue_growth_percent and expansion_cost are required"
                )
        return input_data
