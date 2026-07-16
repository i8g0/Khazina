"""AI provider factory — single configuration switch for inference backend."""

from __future__ import annotations

from app.ai.config import get_ai_settings
from app.ai.exceptions import AIConfigurationError
from app.ai.providers.base import AIProvider
from app.ai.providers.cloud import CloudProvider
from app.ai.providers.ollama import OllamaProvider
from app.core.config.ai import AiSettings


def create_ai_provider(ai_settings: AiSettings | None = None) -> AIProvider:
    """Instantiate the configured AI provider.

    Selection is driven exclusively by ``AI_PROVIDER`` (``ollama`` | ``cloud``).
    """
    settings = ai_settings or get_ai_settings()
    provider = settings.ai_provider.strip().lower()
    if provider == "ollama":
        return OllamaProvider(settings)
    if provider == "cloud":
        return CloudProvider(settings)
    raise AIConfigurationError(
        f"Unsupported AI_PROVIDER '{settings.ai_provider}'. Expected 'ollama' or 'cloud'."
    )
