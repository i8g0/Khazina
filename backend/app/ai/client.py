"""AI HTTP client — backward-compatible entry point delegating to provider layer."""

from __future__ import annotations

from app.ai.providers.ollama import OllamaProvider


class OllamaClient(OllamaProvider):
    """Backward-compatible alias for :class:`OllamaProvider`.

    New code should use :func:`app.ai.providers.create_ai_provider` instead.
    """
