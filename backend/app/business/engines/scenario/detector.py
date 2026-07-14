"""Scenario Engine — minimal detection layer (impact directions)."""

from __future__ import annotations

from dataclasses import dataclass

from app.business.engines.scenario.calculator import ScenarioCalculationResult


@dataclass(frozen=True, slots=True)
class ScenarioDetectionResult:
    overall_direction: str


class ScenarioDetector:
    """Classifies scenario outcome direction from calculation results."""

    def detect(self, calculation: ScenarioCalculationResult) -> ScenarioDetectionResult:
        if calculation.delta_amount > 0:
            direction = "up"
        elif calculation.delta_amount < 0:
            direction = "down"
        else:
            direction = "neutral"
        return ScenarioDetectionResult(overall_direction=direction)
