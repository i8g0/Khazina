"""AI provider interface — single abstraction for all inference backends."""

from __future__ import annotations

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Minimal contract for LLM completion, health, and availability.

    Business services, prompt engine, and parsers depend on this interface only.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Stable provider identifier (e.g. ``ollama``, ``cloud``)."""

    @property
    @abstractmethod
    def configured_model(self) -> str:
        """Active model identifier for this deployment."""

    @property
    @abstractmethod
    def timeout_seconds(self) -> float:
        """HTTP/request timeout in seconds."""

    @abstractmethod
    def check_connectivity(self) -> None:
        """Verify provider availability without running inference.

        Raises:
            AIConnectionError: endpoint unreachable or unhealthy.
            AITimeoutError: probe exceeded timeout.
        """

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        format_json: bool = False,
        think: bool = False,
    ) -> str:
        """Generate a chat completion and return assistant text.

        Raises:
            AIConfigurationError: invalid request configuration.
            AIConnectionError: transport or provider error.
            AITimeoutError: request exceeded timeout.
        """

    def close(self) -> None:
        """Release pooled connections; default no-op."""
