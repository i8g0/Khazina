"""AI orchestrator types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ai.context.types import PromptContext
from app.ai.parsers.types import ParsedResponse
from app.ai.prompts.composer import ComposedPrompt
from app.ai.prompts.tasks import PromptTask
from app.business.facts.contract import FactsContract


@dataclass(frozen=True, slots=True)
class AiExecutionRequest:
    """Single orchestrated AI execution request."""

    engine_id: str
    engine_input: Any
    task: PromptTask
    conversation_id: str | None = None
    prompt_language: str | None = None
    domain: str | None = None
    max_facts: int | None = None
    request_json_response: bool = False
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AiExecutionResult:
    """Structured result from a complete AI pipeline execution."""

    conversation_id: str
    facts_contract: FactsContract
    prompt_context: PromptContext
    composed_prompt: ComposedPrompt
    llm_response_text: str
    parsed_response: ParsedResponse
    extensions: dict[str, Any] = field(default_factory=dict)
