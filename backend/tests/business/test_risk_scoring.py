"""Risk scoring unit tests."""

from __future__ import annotations

import pytest

from app.business.engines.risk.scoring import (
    classify_posture,
    priority_from_score,
    score_risk,
)
from app.db.models.enums import RiskLevel, RiskPriority


@pytest.mark.parametrize(
    ("likelihood", "impact", "expected"),
    [
        (RiskLevel.LOW, RiskLevel.LOW, 20),
        (RiskLevel.MEDIUM, RiskLevel.HIGH, 70),
        (RiskLevel.HIGH, RiskLevel.HIGH, 90),
    ],
)
def test_score_risk_matrix(likelihood: str, impact: str, expected: int) -> None:
    assert score_risk(likelihood, impact) == expected


def test_score_risk_reproducible() -> None:
    first = score_risk(RiskLevel.MEDIUM, RiskLevel.MEDIUM)
    second = score_risk(RiskLevel.MEDIUM, RiskLevel.MEDIUM)
    assert first == second == 55


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (90, RiskPriority.HIGH),
        (70, RiskPriority.HIGH),
        (55, RiskPriority.MEDIUM),
        (40, RiskPriority.MEDIUM),
        (20, RiskPriority.LOW),
    ],
)
def test_priority_from_score(score: int, expected: str) -> None:
    assert priority_from_score(score) == expected


def test_classify_posture_elevated() -> None:
    assert classify_posture(high_count=2, medium_count=0, max_score=75) == "elevated"


def test_classify_posture_low() -> None:
    assert classify_posture(high_count=0, medium_count=0, max_score=20) == "low"
