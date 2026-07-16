"""AI infrastructure package (Sprint 5.1 / Phase 10).

Business services depend on the provider interface; inference backends live under
``app.ai.providers``.
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
from app.ai.health import AiHealthResult, check_ai_provider_health, check_ollama_health
from app.ai.providers import AIProvider, CloudProvider, OllamaProvider, create_ai_provider
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
    "AIProvider",
    "AITimeoutError",
    "AiExecutionRequest",
    "AiExecutionResult",
    "AiHealthResult",
    "AiOrchestrator",
    "CloudProvider",
    "ContextBuildOptions",
    "ContextBuilder",
    "ConversationNotFoundError",
    "ConversationService",
    "OrchestrationError",
    "OllamaClient",
    "OllamaProvider",
    "ParsedResponse",
    "PromptContext",
    "ResponseParseError",
    "ResponseParser",
    "check_ai_provider_health",
    "check_ollama_health",
    "create_ai_provider",
]
