"""Ollama inference provider."""

from __future__ import annotations

import httpx

from app.ai.config import get_ai_settings
from app.ai.exceptions import AIConfigurationError, AIConnectionError, AITimeoutError
from app.ai.providers.base import AIProvider
from app.core.config.ai import AiSettings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaProvider(AIProvider):
    """Ollama HTTP provider — ``GET /api/tags`` health, ``POST /api/chat`` completion."""

    def __init__(self, ai_settings: AiSettings | None = None) -> None:
        self._settings = ai_settings or get_ai_settings()
        self._ensure_ollama_config()
        self._base_url = str(self._settings.ollama_url).rstrip("/")
        self._http: httpx.Client | None = None

    def _ensure_ollama_config(self) -> None:
        if self._settings.ollama_url is None:
            raise AIConfigurationError("OLLAMA_URL is required for Ollama provider")
        if not (self._settings.ollama_model or "").strip():
            raise AIConfigurationError("OLLAMA_MODEL is required for Ollama provider")

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def configured_model(self) -> str:
        return self._settings.ollama_model or ""

    @property
    def timeout_seconds(self) -> float:
        return self._settings.ai_timeout

    def _client(self) -> httpx.Client:
        if self._http is None or self._http.is_closed:
            self._http = httpx.Client(timeout=self._settings.ai_timeout)
        return self._http

    def close(self) -> None:
        if self._http is not None and not self._http.is_closed:
            self._http.close()
        self._http = None

    def check_connectivity(self) -> None:
        url = f"{self._base_url}/api/tags"
        try:
            response = self._client().get(url)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise AITimeoutError(
                f"Ollama request timed out after {self._settings.ai_timeout}s"
            ) from exc
        except httpx.HTTPError as exc:
            logger.warning("Ollama connectivity check failed: %s", exc)
            raise AIConnectionError("Ollama endpoint is unreachable") from exc

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        format_json: bool = False,
        think: bool = False,
    ) -> str:
        if not messages:
            raise AIConfigurationError("At least one chat message is required")

        payload: dict[str, object] = {
            "model": model or self.configured_model,
            "messages": messages,
            "stream": False,
            "think": think,
        }
        if format_json:
            payload["format"] = "json"

        url = f"{self._base_url}/api/chat"
        try:
            response = self._client().post(url, json=payload)
            response.raise_for_status()
            body = response.json()
        except httpx.TimeoutException as exc:
            raise AITimeoutError(
                f"Ollama request timed out after {self._settings.ai_timeout}s"
            ) from exc
        except httpx.HTTPError as exc:
            logger.warning("Ollama chat request failed: %s", exc)
            raise AIConnectionError("Ollama chat request failed") from exc

        message = body.get("message")
        if not isinstance(message, dict):
            raise AIConnectionError("Ollama chat response missing message payload")
        content = message.get("content")
        if not isinstance(content, str):
            raise AIConnectionError("Ollama chat response missing assistant content")
        return content
