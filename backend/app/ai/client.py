"""Ollama HTTP client — the only module that communicates with Ollama (Sprint 5.1)."""

from __future__ import annotations

import httpx

from app.ai.config import get_ai_settings
from app.ai.exceptions import AIConfigurationError, AIConnectionError, AITimeoutError
from app.core.config.ai import AiSettings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Dedicated Ollama connectivity client. No generation or prompt logic."""

    def __init__(self, ai_settings: AiSettings | None = None) -> None:
        self._settings = ai_settings or get_ai_settings()
        self._base_url = str(self._settings.ollama_url).rstrip("/")
        if not self._base_url:
            raise AIConfigurationError("OLLAMA_URL must not be empty")

    @property
    def configured_model(self) -> str:
        return self._settings.ollama_model

    @property
    def timeout_seconds(self) -> float:
        return self._settings.ai_timeout

    def check_connectivity(self) -> None:
        """Verify that the configured Ollama endpoint responds.

        Uses ``GET /api/tags`` — connectivity check only; no model generation.
        """
        url = f"{self._base_url}/api/tags"
        try:
            with httpx.Client(timeout=self._settings.ai_timeout) as client:
                response = client.get(url)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise AITimeoutError(
                f"Ollama request timed out after {self._settings.ai_timeout}s"
            ) from exc
        except httpx.HTTPError as exc:
            logger.debug("Ollama connectivity check failed: %s", exc)
            raise AIConnectionError("Ollama endpoint is unreachable") from exc

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        format_json: bool = False,
    ) -> str:
        """Send a chat completion request to Ollama and return assistant content."""
        if not messages:
            raise AIConfigurationError("At least one chat message is required")

        payload: dict[str, object] = {
            "model": model or self.configured_model,
            "messages": messages,
            "stream": False,
        }
        if format_json:
            payload["format"] = "json"

        url = f"{self._base_url}/api/chat"
        try:
            with httpx.Client(timeout=self._settings.ai_timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.TimeoutException as exc:
            raise AITimeoutError(
                f"Ollama request timed out after {self._settings.ai_timeout}s"
            ) from exc
        except httpx.HTTPError as exc:
            logger.debug("Ollama chat request failed: %s", exc)
            raise AIConnectionError("Ollama chat request failed") from exc

        message = body.get("message")
        if not isinstance(message, dict):
            raise AIConnectionError("Ollama chat response missing message payload")
        content = message.get("content")
        if not isinstance(content, str):
            raise AIConnectionError("Ollama chat response missing assistant content")
        return content
