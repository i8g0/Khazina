"""Cloud inference provider — OpenAI-compatible chat completions API."""

from __future__ import annotations

import threading
import time

import httpx

from app.ai.config import get_ai_settings
from app.ai.exceptions import AIConfigurationError, AIConnectionError, AITimeoutError
from app.ai.providers.base import AIProvider
from app.ai.task_context import get_current_ai_task
from app.ai.telemetry import record_ai_request
from app.core.config.ai import AiSettings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CloudProvider(AIProvider):
    """Provider-agnostic cloud backend using OpenAI-compatible ``/chat/completions``.

    Works with OpenAI, Azure OpenAI, Anthropic-compatible gateways, Gemini OpenAI
    adapters, and other vendors that expose the same HTTP contract — switch vendor
    by changing ``CLOUD_AI_BASE_URL``, ``CLOUD_AI_MODEL``, and ``CLOUD_AI_API_KEY``.
    """

    def __init__(self, ai_settings: AiSettings | None = None) -> None:
        self._settings = ai_settings or get_ai_settings()
        self._ensure_cloud_config()
        self._base_url = str(self._settings.cloud_ai_base_url).rstrip("/")
        self._thread_local = threading.local()

    def _ensure_cloud_config(self) -> None:
        if self._settings.cloud_ai_base_url is None:
            raise AIConfigurationError("CLOUD_AI_BASE_URL is required for cloud provider")
        if not (self._settings.cloud_ai_model or "").strip():
            raise AIConfigurationError("CLOUD_AI_MODEL is required for cloud provider")
        if not (self._settings.cloud_ai_api_key or "").strip():
            raise AIConfigurationError("CLOUD_AI_API_KEY is required for cloud provider")

    @property
    def provider_name(self) -> str:
        return "cloud"

    @property
    def configured_model(self) -> str:
        return self._settings.cloud_ai_model or ""

    @property
    def timeout_seconds(self) -> float:
        return self._settings.ai_timeout

    def _client(self) -> httpx.Client:
        """Thread-local HTTP client — safe for parallel task execution."""
        client = getattr(self._thread_local, "http", None)
        if client is None or client.is_closed:
            client = httpx.Client(timeout=self._settings.ai_timeout)
            self._thread_local.http = client
        return client

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        api_key = self._settings.cloud_ai_api_key
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _chat_url(self) -> str:
        return f"{self._base_url}/chat/completions"

    def _models_url(self) -> str:
        return f"{self._base_url}/models"

    def close(self) -> None:
        client = getattr(self._thread_local, "http", None)
        if client is not None and not client.is_closed:
            client.close()
        self._thread_local.http = None

    def check_connectivity(self) -> None:
        """Probe ``GET /models`` when available; fall back to lightweight base reachability."""
        try:
            response = self._client().get(self._models_url(), headers=self._headers())
            if response.status_code == 404:
                response = self._client().get(self._base_url, headers=self._headers())
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise AITimeoutError(
                f"Cloud AI request timed out after {self._settings.ai_timeout}s"
            ) from exc
        except httpx.HTTPError as exc:
            logger.warning("Cloud AI connectivity check failed: %s", exc)
            raise AIConnectionError("Cloud AI endpoint is unreachable") from exc

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        format_json: bool = False,
        think: bool = False,
    ) -> str:
        del think  # cloud adapters may not support local thinking flags

        if not messages:
            raise AIConfigurationError("At least one chat message is required")

        active_model = model or self.configured_model
        endpoint = self._chat_url()
        payload: dict[str, object] = {
            "model": active_model,
            "messages": messages,
            "temperature": self._settings.ai_temperature,
            "stream": False,
        }
        if format_json:
            payload["response_format"] = {"type": "json_object"}

        started = time.perf_counter()
        try:
            response = self._client().post(
                endpoint,
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            body = response.json()
        except httpx.TimeoutException as exc:
            raise AITimeoutError(
                f"Cloud AI request timed out after {self._settings.ai_timeout}s"
            ) from exc
        except httpx.HTTPError as exc:
            logger.warning("Cloud AI chat request failed: %s", exc)
            raise AIConnectionError("Cloud AI chat request failed") from exc

        latency_ms = (time.perf_counter() - started) * 1000
        usage = body.get("usage") if isinstance(body, dict) else None
        prompt_tokens = (
            int(usage["prompt_tokens"])
            if isinstance(usage, dict) and isinstance(usage.get("prompt_tokens"), int)
            else None
        )
        completion_tokens = (
            int(usage["completion_tokens"])
            if isinstance(usage, dict) and isinstance(usage.get("completion_tokens"), int)
            else None
        )
        record_ai_request(
            provider=self.provider_name,
            model=active_model,
            endpoint=endpoint,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            task=get_current_ai_task(),
        )

        choices = body.get("choices")
        if not isinstance(choices, list) or not choices:
            raise AIConnectionError("Cloud AI response missing choices payload")
        first = choices[0]
        if not isinstance(first, dict):
            raise AIConnectionError("Cloud AI response choice is invalid")
        message = first.get("message")
        if not isinstance(message, dict):
            raise AIConnectionError("Cloud AI response missing message payload")
        content = message.get("content")
        if not isinstance(content, str):
            raise AIConnectionError("Cloud AI response missing assistant content")
        return content
