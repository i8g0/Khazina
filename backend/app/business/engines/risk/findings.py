"""Risk finding types — analytical outputs, not register rows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CandidateFinding:
    """Pre-scored detection emitted by a category rule module."""

    category_code: str
    name: str
    description: str
    likelihood: str
    impact: str
    detection_rule_id: str
    evidence: dict[str, Any]


@dataclass(frozen=True, slots=True)
class RiskFinding:
    """Scored, classified finding ready for persistence or review."""

    finding_id: str
    category_code: str
    name: str
    description: str
    likelihood: str
    impact: str
    score: int
    priority: str
    detection_rule_id: str
    evidence: dict[str, Any]
    finding_status: str = "detected"

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "category_code": self.category_code,
            "name": self.name,
            "description": self.description,
            "likelihood": self.likelihood,
            "impact": self.impact,
            "score": self.score,
            "priority": self.priority,
            "detection_rule_id": self.detection_rule_id,
            "evidence": dict(self.evidence),
            "finding_status": self.finding_status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RiskFinding:
        return cls(
            finding_id=str(data["finding_id"]),
            category_code=str(data["category_code"]),
            name=str(data["name"]),
            description=str(data["description"]),
            likelihood=str(data["likelihood"]),
            impact=str(data["impact"]),
            score=int(data["score"]),
            priority=str(data["priority"]),
            detection_rule_id=str(data["detection_rule_id"]),
            evidence=dict(data.get("evidence") or {}),
            finding_status=str(data.get("finding_status", "detected")),
        )
