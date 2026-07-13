"""Waste Detector — threshold-based business event detection."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.business.engines.waste.calculator import WasteCalculationResult


class WasteLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class WasteDetectionEvent:
    event_type: str
    classification: WasteLevel
    metric: str
    value: str
    threshold_applied: str


@dataclass(frozen=True, slots=True)
class WasteCategoryDetection:
    category_name: str
    waste_level: WasteLevel


@dataclass(frozen=True, slots=True)
class WasteDetectionResult:
    overall_waste_level: WasteLevel
    category_detections: tuple[WasteCategoryDetection, ...]
    events: tuple[WasteDetectionEvent, ...]


class WasteDetector:
    """Detects waste severity classifications from calculated metrics."""

    OVERALL_HIGH_THRESHOLD = Decimal("10.00")
    OVERALL_MEDIUM_THRESHOLD = Decimal("5.00")
    CATEGORY_HIGH_THRESHOLD = Decimal("30.00")
    CATEGORY_MEDIUM_THRESHOLD = Decimal("15.00")

    def detect(self, calculation: WasteCalculationResult) -> WasteDetectionResult:
        overall_level = self._classify_overall(calculation.waste_percentage)
        category_detections: list[WasteCategoryDetection] = []
        events: list[WasteDetectionEvent] = [
            WasteDetectionEvent(
                event_type="waste_level_classification",
                classification=overall_level,
                metric="waste.percentage",
                value=str(calculation.waste_percentage),
                threshold_applied=self._overall_threshold_label(overall_level),
            )
        ]

        for category in calculation.categories:
            level = self._classify_category(category.percentage_of_waste)
            category_detections.append(
                WasteCategoryDetection(
                    category_name=category.category_name,
                    waste_level=level,
                )
            )
            events.append(
                WasteDetectionEvent(
                    event_type="category_waste_level_classification",
                    classification=level,
                    metric="waste.category_percentage",
                    value=str(category.percentage_of_waste),
                    threshold_applied=self._category_threshold_label(level),
                )
            )

        return WasteDetectionResult(
            overall_waste_level=overall_level,
            category_detections=tuple(category_detections),
            events=tuple(events),
        )

    def _classify_overall(self, waste_percentage: Decimal) -> WasteLevel:
        if waste_percentage >= self.OVERALL_HIGH_THRESHOLD:
            return WasteLevel.HIGH
        if waste_percentage >= self.OVERALL_MEDIUM_THRESHOLD:
            return WasteLevel.MEDIUM
        return WasteLevel.LOW

    def _classify_category(self, category_share: Decimal) -> WasteLevel:
        if category_share >= self.CATEGORY_HIGH_THRESHOLD:
            return WasteLevel.HIGH
        if category_share >= self.CATEGORY_MEDIUM_THRESHOLD:
            return WasteLevel.MEDIUM
        return WasteLevel.LOW

    @staticmethod
    def _overall_threshold_label(level: WasteLevel) -> str:
        if level is WasteLevel.HIGH:
            return "overall_waste_percentage>=10.00"
        if level is WasteLevel.MEDIUM:
            return "overall_waste_percentage>=5.00"
        return "overall_waste_percentage<5.00"

    @staticmethod
    def _category_threshold_label(level: WasteLevel) -> str:
        if level is WasteLevel.HIGH:
            return "category_share_of_waste>=30.00"
        if level is WasteLevel.MEDIUM:
            return "category_share_of_waste>=15.00"
        return "category_share_of_waste<15.00"
