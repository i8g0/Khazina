"""Waste Detector unit tests."""

from __future__ import annotations

from decimal import Decimal

from app.business.engines.waste.calculator import (
    WasteCalculationResult,
    WasteCategoryCalculation,
)
from app.business.engines.waste.detector import WasteDetector, WasteLevel


def _calculation(waste_percentage: str) -> WasteCalculationResult:
    return WasteCalculationResult(
        total_spend=Decimal("100.00"),
        total_waste_amount=Decimal("10.00"),
        waste_percentage=Decimal(waste_percentage),
        categories=(
            WasteCategoryCalculation("a", Decimal("3.00"), Decimal("30.00")),
            WasteCategoryCalculation("b", Decimal("1.50"), Decimal("15.00")),
            WasteCategoryCalculation("c", Decimal("0.50"), Decimal("5.00")),
        ),
        top_category_name="a",
        top_category_percentage=Decimal("30.00"),
        recoverable_savings_rate=Decimal("0.80"),
        potential_savings_amount=Decimal("8.00"),
        active_savings_opportunities=2,
    )


def test_detector_classifies_overall_and_category_levels() -> None:
    detector = WasteDetector()
    result = detector.detect(_calculation("4.80"))

    assert result.overall_waste_level is WasteLevel.LOW
    assert result.category_detections[0].waste_level is WasteLevel.HIGH
    assert result.category_detections[1].waste_level is WasteLevel.MEDIUM
    assert result.category_detections[2].waste_level is WasteLevel.LOW
    assert len(result.events) == 4


def test_detector_high_overall_threshold() -> None:
    detector = WasteDetector()
    result = detector.detect(_calculation("12.00"))
    assert result.overall_waste_level is WasteLevel.HIGH


def test_detector_medium_overall_threshold() -> None:
    detector = WasteDetector()
    result = detector.detect(_calculation("7.50"))
    assert result.overall_waste_level is WasteLevel.MEDIUM
