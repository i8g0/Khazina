"""Benchmark-only Ollama client — isolated timeout and thinking options."""

from __future__ import annotations

import httpx

from scripts.ai_benchmark.config import BenchmarkConfig


class BenchmarkOllamaClient:
    """Ollama HTTP access for benchmarks only. Does not modify production ``OllamaClient``."""

    def __init__(self, config: BenchmarkConfig) -> None:
        self._config = config
        self._base_url = config.ollama_url.rstrip("/")

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        thinking_enabled: bool = False,
        format_json: bool = False,
    ) -> str:
        payload: dict[str, object] = {
            "model": self._config.ollama_model,
            "messages": messages,
            "stream": False,
            "think": thinking_enabled,
        }
        if format_json:
            payload["format"] = "json"

        url = f"{self._base_url}/api/chat"
        with httpx.Client(timeout=self._config.benchmark_timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()

        message = body.get("message")
        if not isinstance(message, dict):
            raise RuntimeError("Ollama chat response missing message payload")
        content = message.get("content")
        if not isinstance(content, str):
            raise RuntimeError("Ollama chat response missing assistant content")
        return content

    def unload_model(self) -> None:
        """Unload model from memory using keep_alive=0."""
        payload = {
            "model": self._config.ollama_model,
            "messages": [{"role": "user", "content": "ping"}],
            "stream": False,
            "keep_alive": 0,
            "think": False,
        }
        url = f"{self._base_url}/api/chat"
        try:
            with httpx.Client(timeout=min(self._config.benchmark_timeout, 120.0)) as client:
                client.post(url, json=payload)
        except httpx.HTTPError:
            pass
