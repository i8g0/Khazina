"""Single-task AI pipeline composing frozen Phase 5 components."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Protocol

from app.ai.context.builder import ContextBuilder
from app.ai.context.types import ContextBuildOptions
from app.ai.task_context import reset_current_ai_task, set_current_ai_task
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
        llm_client: _ChatClient | None = None,
        llm_model: str | None = None,
        ollama_client: _ChatClient | None = None,
        ollama_model: str | None = None,
        prompt_language: str | None = None,
    ) -> None:
        self._context_builder = context_builder or ContextBuilder()
        self._prompt_composer = prompt_composer or PromptComposer()
        self._response_parser = response_parser or ResponseParser()
        self._llm = llm_client or ollama_client
        self._llm_model = llm_model or ollama_model
        self._prompt_language = prompt_language

    def execute_task(
        self,
        facts_contract: FactsContract,
        task: PromptTask,
        *,
        domain: str = "waste",
        prompt_language: str | None = None,
        prompt_supplement: str | None = None,
    ) -> TaskExecutionResult:
        if self._llm is None:
            raise AiRecommendationError(
                "llm_unavailable",
                "AI provider is not configured",
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
            {
                "role": "user",
                "content": (
                    f"{composed.user_prompt.rstrip()}\n\n{prompt_supplement.rstrip()}\n"
                    if prompt_supplement
                    else composed.user_prompt
                ),
            },
        ]
        task_token = set_current_ai_task(task.value)
        try:
            llm_response = self._llm.chat(messages, model=self._llm_model)
        finally:
            reset_current_ai_task(task_token)
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

    def execute_tasks(
        self,
        facts_contract: FactsContract,
        tasks: tuple[PromptTask, ...],
        *,
        domain: str = "waste",
        prompt_language: str | None = None,
        prompt_supplement: str | None = None,
        parallel: bool = False,
        max_workers: int | None = None,
    ) -> tuple[TaskExecutionResult, ...]:
        """Execute multiple tasks — sequentially or in parallel when safe."""
        if not tasks:
            return ()
        if not parallel or len(tasks) == 1:
            return tuple(
                self.execute_task(
                    facts_contract,
                    task,
                    domain=domain,
                    prompt_language=prompt_language,
                    prompt_supplement=prompt_supplement,
                )
                for task in tasks
            )

        workers = max_workers or min(len(tasks), 8)
        results: dict[PromptTask, TaskExecutionResult] = {}

        def _run(task: PromptTask) -> TaskExecutionResult:
            return self.execute_task(
                facts_contract,
                task,
                domain=domain,
                prompt_language=prompt_language,
                prompt_supplement=prompt_supplement,
            )

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_run, task): task for task in tasks}
            for future in as_completed(futures):
                result = future.result()
                results[result.task] = result

        return tuple(results[task] for task in tasks)
