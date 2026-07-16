"""AI Recommendation Service errors."""

from __future__ import annotations

from typing import Any


class AiRecommendationError(Exception):
    """Deterministic AI recommendation mapping or pipeline failure."""

    def __init__(
        self,
        error_code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(f"{error_code}: {message}")

    def to_failure_details(self) -> dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            **self.details,
        }
