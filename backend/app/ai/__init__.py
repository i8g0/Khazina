"""AI infrastructure package (Sprint 5.1).

Isolated from repositories, business services, and routers. All Ollama
communication is confined to ``app.ai.client``.
"""

from app.ai.client import OllamaClient
from app.ai.exceptions import (
    AIConfigurationError,
    AIConnectionError,
    AIError,
    AITimeoutError,
)
from app.ai.health import AiHealthResult, check_ollama_health

__all__ = [
    "AIConfigurationError",
    "AIConnectionError",
    "AIError",
    "AITimeoutError",
    "AiHealthResult",
    "OllamaClient",
    "check_ollama_health",
]
