"""AI layer configuration access."""

from __future__ import annotations

from app.core.config.ai import AiSettings


def get_ai_settings() -> AiSettings:
    """Return the application AI settings singleton."""
    from app.core.config import settings

    return settings.ai


__all__ = ["AiSettings", "get_ai_settings"]
