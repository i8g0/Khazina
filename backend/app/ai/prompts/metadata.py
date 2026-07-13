"""Centralized Prompt Metadata creation (architecture standard)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.ai.prompts.tasks import PromptTask
from app.ai.prompts.version import PROMPT_VERSION


@dataclass(frozen=True, slots=True)
class PromptMetadata:
    """Internal system metadata — not part of prompt instructions."""

    prompt_version: str
    prompt_language: str
    task: PromptTask
    created_at: datetime
    extensions: dict[str, Any] = field(default_factory=dict)


def build_prompt_metadata(
    *,
    task: PromptTask,
    prompt_language: str,
    created_at: datetime | None = None,
    **extensions: Any,
) -> PromptMetadata:
    """Create prompt metadata. PromptComposer is the sole caller in production."""
    return PromptMetadata(
        prompt_version=PROMPT_VERSION,
        prompt_language=prompt_language,
        task=task,
        created_at=created_at or datetime.now(UTC),
        extensions=dict(extensions),
    )
