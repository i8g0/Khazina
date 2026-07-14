"""AI Recommendation Service errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class AiRecommendationError(Exception):
    """Deterministic AI recommendation mapping or pipeline failure."""

    error_code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"

    def to_failure_details(self) -> dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            **self.details,
        }
