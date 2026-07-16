"""AI Orchestrator — coordinates Business Engines through LLM invocation."""

from __future__ import annotations

from typing import Any, Protocol

from app.ai.providers.factory import create_ai_provider
from app.ai.context.builder import ContextBuilder
from app.ai.context.types import ContextBuildOptions
from app.ai.parsers.response_parser import ResponseParser
from app.ai.prompts.composer import PromptComposer
from app.ai.services.conversation import ConversationService
from app.ai.services.types import AiExecutionRequest, AiExecutionResult
from app.business.registry import get_engine


class _ChatClient(Protocol):
    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        format_json: bool = False,
    ) -> str: ...


class AiOrchestrator:
    """Coordinates engine execution, context building, prompting, and parsing."""

    def __init__(
        self,
        *,
        context_builder: ContextBuilder | None = None,
        prompt_composer: PromptComposer | None = None,
        conversation_service: ConversationService | None = None,
        response_parser: ResponseParser | None = None,
        llm_client: _ChatClient | None = None,
        ollama_client: _ChatClient | None = None,
        engine_resolver: Any | None = None,
    ) -> None:
        self._context_builder = context_builder or ContextBuilder()
        self._prompt_composer = prompt_composer or PromptComposer()
        self._conversations = conversation_service or ConversationService()
        self._response_parser = response_parser or ResponseParser()
        self._llm = llm_client or ollama_client or create_ai_provider()
        self._resolve_engine = engine_resolver or get_engine

    @property
    def conversation_service(self) -> ConversationService:
        return self._conversations

    def execute(self, request: AiExecutionRequest) -> AiExecutionResult:
        conversation = self._conversations.get_or_create(
            request.conversation_id,
            engine_id=request.engine_id,
        )

        engine = self._resolve_engine(request.engine_id)
        facts_contract = engine.run(request.engine_input)

        prompt_context = self._context_builder.build(
            facts_contract,
            ContextBuildOptions(
                task=request.task,
                domain=request.domain,
                max_facts=request.max_facts,
            ),
        )

        composed_prompt = self._prompt_composer.compose(
            request.task,
            prompt_context.facts,
            prompt_language=request.prompt_language,
        )

        messages: list[dict[str, str]] = [
            {"role": "system", "content": composed_prompt.system_prompt},
            *self._conversations.history_messages(conversation.id),
            {"role": "user", "content": composed_prompt.user_prompt},
        ]

        llm_response = self._llm.chat(
            messages,
            format_json=request.request_json_response,
        )
        parsed_response = self._response_parser.parse(llm_response)

        self._conversations.append_turn(
            conversation.id,
            role="user",
            content=composed_prompt.user_prompt,
            metadata={"task": request.task.value, "engine_id": request.engine_id},
        )
        self._conversations.append_turn(
            conversation.id,
            role="assistant",
            content=llm_response,
            metadata={"task": request.task.value, "engine_id": request.engine_id},
        )

        return AiExecutionResult(
            conversation_id=conversation.id,
            facts_contract=facts_contract,
            prompt_context=prompt_context,
            composed_prompt=composed_prompt,
            llm_response_text=llm_response,
            parsed_response=parsed_response,
            extensions=dict(request.extensions),
        )
