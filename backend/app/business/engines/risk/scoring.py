"""Deterministic risk scoring — likelihood × impact matrix (Sprint 9.2).

Scoring formula (locked for reproducibility):

1. Map likelihood L ∈ {low, medium, high} and impact I ∈ {low, medium, high}
   to a base score using the 3×3 matrix below.
2. Clamp result to [0, 100].
3. Derive priority band:
   - high:   score >= 70
   - medium: 40 <= score < 70
   - low:    score < 40

No randomness. No AI. Same inputs always produce the same score.
"""

from __future__ import annotations

from app.db.models.enums import RiskLevel, RiskPriority

# (likelihood, impact) → score
_SCORE_MATRIX: dict[tuple[str, str], int] = {
    (RiskLevel.LOW, RiskLevel.LOW): 20,
    (RiskLevel.LOW, RiskLevel.MEDIUM): 35,
    (RiskLevel.LOW, RiskLevel.HIGH): 50,
    (RiskLevel.MEDIUM, RiskLevel.LOW): 40,
    (RiskLevel.MEDIUM, RiskLevel.MEDIUM): 55,
    (RiskLevel.MEDIUM, RiskLevel.HIGH): 70,
    (RiskLevel.HIGH, RiskLevel.LOW): 60,
    (RiskLevel.HIGH, RiskLevel.MEDIUM): 75,
    (RiskLevel.HIGH, RiskLevel.HIGH): 90,
}

_PRIORITY_HIGH_THRESHOLD = 70
_PRIORITY_MEDIUM_THRESHOLD = 40


def score_risk(likelihood: str, impact: str) -> int:
    """Return deterministic composite score 0–100."""
    key = (likelihood, impact)
    if key not in _SCORE_MATRIX:
        raise ValueError(f"Unknown likelihood/impact pair: {key}")
    return _SCORE_MATRIX[key]


def priority_from_score(score: int) -> str:
    """Map numeric score to executive priority band."""
    if score >= _PRIORITY_HIGH_THRESHOLD:
        return RiskPriority.HIGH
    if score >= _PRIORITY_MEDIUM_THRESHOLD:
        return RiskPriority.MEDIUM
    return RiskPriority.LOW


def classify_posture(high_count: int, medium_count: int, max_score: int) -> str:
    """Overall org risk posture from finding aggregates."""
    from app.business.engines.risk.constants import (
        POSTURE_ELEVATED,
        POSTURE_LOW,
        POSTURE_MODERATE,
    )

    if high_count >= 2 or max_score >= 85:
        return POSTURE_ELEVATED
    if high_count >= 1 or medium_count >= 2 or max_score >= 55:
        return POSTURE_MODERATE
    return POSTURE_LOW
