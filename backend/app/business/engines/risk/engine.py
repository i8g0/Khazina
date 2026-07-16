"""Financial Risk Business Engine (Sprint 9.2)."""

from __future__ import annotations

from typing import Any

from app.business.assemblers.risk import RiskFactAssembler
from app.business.base import BusinessEngine
from app.business.engines.risk.calculator import RiskCalculator, RiskCalculationResult
from app.business.engines.risk.detector import RiskDetectionResult, RiskDetector
from app.business.engines.risk.input import RiskEngineInput
from app.business.engines.risk.manifest import RISK_ENGINE_MANIFEST
from app.business.engines.risk.output import RiskEngineOutput
from app.business.exceptions import (
    BusinessRuleViolationError,
    InvalidInputError,
    MissingDataError,
    ValidationError,
)
from app.business.facts.contract import FactsContract
from app.business.manifest import EngineManifest


class RiskEngine(BusinessEngine):
    """Coordinates validation, calculation, detection, scoring, and fact assembly."""

    def __init__(
        self,
        *,
        calculator: RiskCalculator | None = None,
        detector: RiskDetector | None = None,
        assembler: RiskFactAssembler | None = None,
    ) -> None:
        self._calculator = calculator or RiskCalculator()
        self._detector = detector or RiskDetector()
        self._assembler = assembler or RiskFactAssembler()

    @property
    def manifest(self) -> EngineManifest:
        return RISK_ENGINE_MANIFEST

    def run(self, input_data: Any) -> RiskEngineOutput:
        validated = self._validate_input(input_data)
        calculation = self._calculator.calculate(validated)
        detection = self._detector.detect(calculation, validated)
        facts = self.assemble_facts(calculation, detection)
        return RiskEngineOutput(
            facts_contract=facts,
            findings=detection.findings,
            calculation=calculation,
            detection=detection,
        )

    def assemble_facts(
        self,
        calculation_result: Any,
        detection_result: Any,
    ) -> FactsContract:
        if not isinstance(calculation_result, RiskCalculationResult):
            raise InvalidInputError("calculation_result must be RiskCalculationResult")
        if not isinstance(detection_result, RiskDetectionResult):
            raise InvalidInputError("detection_result must be RiskDetectionResult")
        return self._assembler.assemble(calculation_result, detection_result)

    def _validate_input(self, input_data: Any) -> RiskEngineInput:
        if not isinstance(input_data, RiskEngineInput):
            raise InvalidInputError("input_data must be RiskEngineInput")

        if not input_data.organization_id.strip():
            raise ValidationError("organization_id must not be empty")
        if not input_data.snapshot_id.strip():
            raise ValidationError("snapshot_id must not be empty")
        if not input_data.reporting_period.strip():
            raise ValidationError("reporting_period must not be empty")

        metrics = input_data.financial_metrics
        if metrics.total_spend <= 0:
            raise ValidationError("total_spend must be greater than zero")
        if metrics.total_waste_amount < 0:
            raise ValidationError("total_waste_amount must not be negative")
        if metrics.total_waste_amount > metrics.total_spend:
            raise BusinessRuleViolationError(
                "total_waste_amount must not exceed total_spend"
            )
        if not metrics.categories:
            raise MissingDataError("At least one waste category metric is required")

        return input_data
