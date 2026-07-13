"""AI infrastructure package (Sprint 5.1).

Isolated from repositories, business services, and routers. All Ollama
communication is confined to ``app.ai.client``.
"""

from app.ai.client import OllamaClient
from app.ai.context import ContextBuilder, ContextBuildOptions, PromptContext
from app.ai.exceptions import (
    AIConfigurationError,
    AIConnectionError,
    AIError,
    AITimeoutError,
    ConversationNotFoundError,
    OrchestrationError,
    ResponseParseError,
)
from app.ai.health import AiHealthResult, check_ollama_health
from app.ai.parsers import ParsedResponse, ResponseParser
from app.ai.services import (
    AiExecutionRequest,
    AiExecutionResult,
    AiOrchestrator,
    ConversationService,
)

__all__ = [
    "AIConfigurationError",
    "AIConnectionError",
    "AIError",
    "AITimeoutError",
    "AiExecutionRequest",
    "AiExecutionResult",
    "AiHealthResult",
    "AiOrchestrator",
    "ContextBuildOptions",
    "ContextBuilder",
    "ConversationNotFoundError",
    "ConversationService",
    "OrchestrationError",
    "OllamaClient",
    "ParsedResponse",
    "PromptContext",
    "ResponseParseError",
    "ResponseParser",
    "check_ollama_health",
]
