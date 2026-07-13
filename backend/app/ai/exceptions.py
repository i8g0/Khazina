"""AI infrastructure exceptions (Sprint 5.1)."""

from __future__ import annotations


class AIError(Exception):
    """Base class for AI infrastructure errors."""


class AIConfigurationError(AIError):
    """Raised when AI settings or client configuration is invalid."""


class AIConnectionError(AIError):
    """Raised when the Ollama endpoint cannot be reached."""


class AITimeoutError(AIError):
    """Raised when an Ollama request exceeds the configured timeout."""
