"""Context Builder types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ai.prompts.facts import PromptFact
from app.ai.prompts.tasks import PromptTask


@dataclass(frozen=True, slots=True)
class ContextBuildOptions:
    """Deterministic filtering and ordering options for fact selection."""

    task: PromptTask
    domain: str | None = None
    max_facts: int | None = None
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PromptContext:
    """Selected and ordered facts ready for the Prompt Engine."""

    task: PromptTask
    facts: tuple[PromptFact, ...]
    engine_id: str
    contract_version: str
    total_fact_count: int
    selected_fact_count: int
    extensions: dict[str, Any] = field(default_factory=dict)
