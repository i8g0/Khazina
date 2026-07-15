"""Single-task AI pipeline composing frozen Phase 5 components."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.ai.context.builder import ContextBuilder
from app.ai.context.types import ContextBuildOptions
from app.ai.exceptions import ResponseParseError
from app.ai.parsers.response_parser import ResponseParser
from app.ai.parsers.types import ParsedResponse
from app.ai.prompts.composer import ComposedPrompt, PromptComposer
from app.ai.prompts.tasks import PromptTask
from app.ai_recommendations.exceptions import AiRecommendationError
from app.business.facts.contract import FactsContract


class _ChatClient(Protocol):
    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        format_json: bool = False,
    ) -> str: ...


@dataclass(frozen=True, slots=True)
class TaskExecutionResult:
    task: PromptTask
    composed_prompt: ComposedPrompt
    llm_response_text: str
    parsed_response: ParsedResponse


class AiTaskPipeline:
    """Executes one PromptTask against a rehydrated Facts Contract — no business engine execution."""

    def __init__(
        self,
        *,
        context_builder: ContextBuilder | None = None,
        prompt_composer: PromptComposer | None = None,
        response_parser: ResponseParser | None = None,
        ollama_client: _ChatClient | None = None,
        ollama_model: str | None = None,
        prompt_language: str | None = None,
    ) -> None:
        self._context_builder = context_builder or ContextBuilder()
        self._prompt_composer = prompt_composer or PromptComposer()
        self._response_parser = response_parser or ResponseParser()
        self._ollama = ollama_client
        self._ollama_model = ollama_model
        self._prompt_language = prompt_language

    def execute_task(
        self,
        facts_contract: FactsContract,
        task: PromptTask,
        *,
        domain: str = "waste",
        prompt_language: str | None = None,
    ) -> TaskExecutionResult:
        if self._ollama is None:
            raise AiRecommendationError(
                "llm_unavailable",
                "Ollama client is not configured",
            )

        prompt_context = self._context_builder.build(
            facts_contract,
            ContextBuildOptions(task=task, domain=domain),
        )
        composed = self._prompt_composer.compose(
            task,
            prompt_context.facts,
            prompt_language=prompt_language or self._prompt_language,
        )
        messages = [
            {"role": "system", "content": composed.system_prompt},
            {"role": "user", "content": composed.user_prompt},
        ]
        llm_response = self._ollama.chat(messages, model=self._ollama_model)
        if not llm_response.strip():
            raise AiRecommendationError(
                "empty_llm_response",
                f"LLM returned empty response for task '{task.value}'",
            )
        try:
            parsed = self._response_parser.parse(llm_response)
        except ResponseParseError as exc:
            raise AiRecommendationError(
                "response_parse_failed",
                str(exc),
                {"task": task.value},
            ) from exc
        if parsed.format == "json" and parsed.data is None:
            raise AiRecommendationError(
                "unsupported_response_shape",
                f"JSON response unusable for task '{task.value}'",
            )
        return TaskExecutionResult(
            task=task,
            composed_prompt=composed,
            llm_response_text=llm_response,
            parsed_response=parsed,
        )
