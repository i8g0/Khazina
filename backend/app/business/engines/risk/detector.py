"""Risk Detector — orchestrates category rules and applies scoring."""

from __future__ import annotations

import uuid

from app.business.engines.risk.calculator import RiskCalculationResult
from app.business.engines.risk.constants import (
    CATEGORY_FORECAST,
    CATEGORY_STRATEGIC,
    FINDING_STATUS_DETECTED,
)
from app.business.engines.risk.findings import CandidateFinding, RiskFinding
from app.business.engines.risk.input import RiskEngineInput
from app.business.engines.risk.rules import CATEGORY_DETECTORS, EXTENDED_DETECTORS
from app.business.engines.risk.scoring import classify_posture, priority_from_score, score_risk

_FINDING_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _deterministic_finding_id(candidate: CandidateFinding) -> str:
    key = f"{candidate.detection_rule_id}:{candidate.category_code}:{candidate.name}"
    return str(uuid.uuid5(_FINDING_NAMESPACE, key))


class RiskDetectionResult:
    __slots__ = (
        "findings",
        "overall_posture_level",
        "high_count",
        "medium_count",
        "low_count",
    )

    def __init__(
        self,
        findings: tuple[RiskFinding, ...],
        overall_posture_level: str,
        high_count: int,
        medium_count: int,
        low_count: int,
    ) -> None:
        self.findings = findings
        self.overall_posture_level = overall_posture_level
        self.high_count = high_count
        self.medium_count = medium_count
        self.low_count = low_count


class RiskDetector:
    """Runs enabled category rules, scores candidates, emits ordered findings."""

    def detect(
        self, calculation: RiskCalculationResult, input_data: RiskEngineInput
    ) -> RiskDetectionResult:
        enabled = input_data.enabled_categories()
        candidates: list[CandidateFinding] = []

        for category_code, detector in CATEGORY_DETECTORS.items():
            if category_code not in enabled:
                continue
            if category_code in (CATEGORY_STRATEGIC, CATEGORY_FORECAST):
                candidates.extend(detector(calculation, input_data))  # type: ignore[operator]
            else:
                candidates.extend(detector(calculation))  # type: ignore[operator]

        for extended in EXTENDED_DETECTORS:
            candidates.extend(extended(calculation))  # type: ignore[operator]

        scored: list[RiskFinding] = []
        for candidate in candidates:
            score = score_risk(candidate.likelihood, candidate.impact)
            priority = priority_from_score(score)
            scored.append(
                RiskFinding(
                    finding_id=_deterministic_finding_id(candidate),
                    category_code=candidate.category_code,
                    name=candidate.name,
                    description=candidate.description,
                    likelihood=candidate.likelihood,
                    impact=candidate.impact,
                    score=score,
                    priority=priority,
                    detection_rule_id=candidate.detection_rule_id,
                    evidence=dict(candidate.evidence),
                    finding_status=FINDING_STATUS_DETECTED,
                )
            )

        scored.sort(key=lambda item: (-item.score, item.category_code, item.finding_id))
        high = sum(1 for item in scored if item.priority == "high")
        medium = sum(1 for item in scored if item.priority == "medium")
        low = sum(1 for item in scored if item.priority == "low")
        max_score = max((item.score for item in scored), default=0)
        posture = classify_posture(high, medium, max_score)

        return RiskDetectionResult(
            findings=tuple(scored),
            overall_posture_level=posture,
            high_count=high,
            medium_count=medium,
            low_count=low,
        )
