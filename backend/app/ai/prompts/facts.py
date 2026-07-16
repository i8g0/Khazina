"""Prompt-layer fact input for prompt construction (Sprint 5.2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class PromptFact:
    """A single fact prepared for inclusion in a user prompt."""

    domain: str
    metric: str
    value: str
    unit: str | None = None
    severity: str | None = None
    confidence: str | None = None
    source: str | None = None
    period: str | None = None
    organization_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
