"""AI infrastructure health checks (Sprint 5.1)."""

from __future__ import annotations

from dataclasses import dataclass

from app.ai.client import OllamaClient
from app.ai.exceptions import AIConnectionError, AITimeoutError


@dataclass(frozen=True, slots=True)
class AiHealthResult:
    status: str
    ollama_reachable: bool
    configured_model: str
    message: str


def check_ollama_health(client: OllamaClient | None = None) -> AiHealthResult:
    """Check whether the configured Ollama endpoint is reachable.

    Does not perform model generation or inference.
    """
    ollama = client or OllamaClient()
    try:
        ollama.check_connectivity()
    except (AIConnectionError, AITimeoutError) as exc:
        return AiHealthResult(
            status="unavailable",
            ollama_reachable=False,
            configured_model=ollama.configured_model,
            message=str(exc),
        )

    return AiHealthResult(
        status="ok",
        ollama_reachable=True,
        configured_model=ollama.configured_model,
        message="Ollama endpoint is reachable",
    )
