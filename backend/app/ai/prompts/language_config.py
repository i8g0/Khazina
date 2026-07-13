"""Prompt language configuration (architecture standard)."""

from __future__ import annotations

from app.core.config import settings

# Environment variable: DEFAULT_PROMPT_LANGUAGE (see AiSettings.default_prompt_language)


def get_default_prompt_language() -> str:
    """Return the configured default prompt language code (single language per prompt)."""
    return settings.ai.default_prompt_language
