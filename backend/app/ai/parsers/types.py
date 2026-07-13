"""Response parser types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True, slots=True)
class ParsedResponse:
    """Deterministic parse result from an LLM response."""

    format: Literal["json", "text"]
    text: str
    data: dict[str, Any] | list[Any] | None = None
    extensions: dict[str, Any] = field(default_factory=dict)
