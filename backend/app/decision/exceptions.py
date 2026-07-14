"""Decision Engine adapter and orchestration errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SnapshotAdapterError(Exception):
    """Deterministic snapshot mapping failure (§11 contract error codes)."""

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
