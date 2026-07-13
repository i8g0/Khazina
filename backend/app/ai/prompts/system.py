"""Permanent system prompt rules for the Prompt Engine."""

from __future__ import annotations

from app.ai.prompts.language_config import get_default_prompt_language
from app.ai.prompts.languages import get_language_pack


def build_system_prompt(*, prompt_language: str | None = None) -> str:
    """Return the reusable system prompt for a single configured language."""
    language = prompt_language or get_default_prompt_language()
    return get_language_pack(language).system_prompt
