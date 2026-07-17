"""AI infrastructure health checks."""

from __future__ import annotations

from dataclasses import dataclass

from app.ai.exceptions import AIConnectionError, AITimeoutError
from app.ai.providers.base import AIProvider
from app.ai.providers.factory import create_ai_provider


@dataclass(frozen=True, slots=True)
class AiHealthResult:
    status: str
    provider: str
    provider_reachable: bool
    configured_model: str
    message: str
    ollama_reachable: bool


def check_ai_provider_health(provider: AIProvider | None = None) -> AiHealthResult:
    """Check whether the configured AI provider is reachable.

    Does not perform model generation or inference. Never exposes API keys.
    """
    active = provider or create_ai_provider()
    try:
        active.check_connectivity()
    except (AIConnectionError, AITimeoutError) as exc:
        return AiHealthResult(
            status="unavailable",
            provider=active.provider_name,
            provider_reachable=False,
            ollama_reachable=False,
            configured_model=active.configured_model,
            message=str(exc),
        )

    is_ollama = active.provider_name == "ollama"
    return AiHealthResult(
        status="ok",
        provider=active.provider_name,
        provider_reachable=True,
        ollama_reachable=is_ollama,
        configured_model=active.configured_model,
        message=f"{active.provider_name} provider is reachable",
    )


def check_ollama_health(provider: AIProvider | None = None) -> AiHealthResult:
    """Backward-compatible health check entry point."""
    return check_ai_provider_health(provider)
