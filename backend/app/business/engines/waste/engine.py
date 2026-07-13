"""Financial Waste Business Engine (Sprint 5.3B)."""

from __future__ import annotations

from typing import Any

from app.business.assemblers.waste import WasteFactAssembler
from app.business.base import BusinessEngine
from app.business.engines.waste.calculator import WasteCalculator, WasteCalculationResult
from app.business.engines.waste.detector import WasteDetector, WasteDetectionResult
from app.business.engines.waste.input import WasteCategoryInput, WasteEngineInput
from app.business.engines.waste.manifest import WASTE_ENGINE_MANIFEST
from app.business.exceptions import (
    BusinessRuleViolationError,
    InvalidInputError,
    MissingDataError,
    ValidationError,
)
from app.business.facts.contract import FactsContract
from app.business.manifest import EngineManifest


class WasteEngine(BusinessEngine):
    """Coordinates validation, calculation, detection, and fact assembly."""

    def __init__(
        self,
        *,
        calculator: WasteCalculator | None = None,
        detector: WasteDetector | None = None,
        assembler: WasteFactAssembler | None = None,
    ) -> None:
        self._calculator = calculator or WasteCalculator()
        self._detector = detector or WasteDetector()
        self._assembler = assembler or WasteFactAssembler()

    @property
    def manifest(self) -> EngineManifest:
        return WASTE_ENGINE_MANIFEST

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
        if not isinstance(calculation_result, WasteCalculationResult):
            raise InvalidInputError("calculation_result must be WasteCalculationResult")
        if not isinstance(detection_result, WasteDetectionResult):
            raise InvalidInputError("detection_result must be WasteDetectionResult")
        return self._assembler.assemble(calculation_result, detection_result)

    def _validate_input(self, input_data: Any) -> WasteEngineInput:
        if not isinstance(input_data, WasteEngineInput):
            raise InvalidInputError("input_data must be WasteEngineInput")

        if input_data.total_spend <= 0:
            raise ValidationError("total_spend must be greater than zero")

        if input_data.total_waste_amount < 0:
            raise ValidationError("total_waste_amount must not be negative")

        if input_data.total_waste_amount > input_data.total_spend:
            raise BusinessRuleViolationError(
                "total_waste_amount must not exceed total_spend"
            )

        if not input_data.categories:
            raise MissingDataError("At least one waste category is required")

        normalized_categories: list[WasteCategoryInput] = []
        for category in input_data.categories:
            name = category.category_name.strip()
            if not name:
                raise ValidationError("category_name must not be empty")
            if category.amount < 0:
                raise ValidationError("category amount must not be negative")
            normalized_categories.append(
                WasteCategoryInput(category_name=name, amount=category.amount)
            )

        category_total = round(sum(item.amount for item in normalized_categories), 2)
        waste_total = round(input_data.total_waste_amount, 2)
        if category_total != waste_total:
            raise BusinessRuleViolationError(
                "Sum of category amounts must equal total_waste_amount"
            )

        return WasteEngineInput(
            total_spend=input_data.total_spend,
            total_waste_amount=input_data.total_waste_amount,
            categories=tuple(normalized_categories),
            organization_id=input_data.organization_id,
            period=input_data.period,
            source_dataset=input_data.source_dataset.strip() or "waste_analysis",
            generated_at=input_data.generated_at,
        )
