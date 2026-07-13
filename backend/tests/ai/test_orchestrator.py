"""AI Orchestrator end-to-end tests with mocked Ollama."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.ai.prompts.tasks import PromptTask
from app.ai.services.conversation import ConversationService
from app.ai.services.orchestrator import AiOrchestrator
from app.ai.services.types import AiExecutionRequest
from app.business.engines.waste.engine import WasteEngine
from app.business.engines.waste.input import WasteCategoryInput, WasteEngineInput
from app.business.registry import register_engine, reset_registry_for_testing


class _MockOllama:
    def __init__(self, response: str) -> None:
        self.response = response
        self.messages: list[dict[str, str]] = []

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        format_json: bool = False,
    ) -> str:
        self.messages = messages
        return self.response


@pytest.fixture(autouse=True)
def _reset_registry() -> None:
    reset_registry_for_testing()
    register_engine(WasteEngine())


def _waste_input() -> WasteEngineInput:
    return WasteEngineInput(
        total_spend=50_000_000.0,
        total_waste_amount=2_340_000.0,
        categories=(
            WasteCategoryInput("overlapping_contracts", 745_000.0),
            WasteCategoryInput("operations", 520_000.0),
            WasteCategoryInput("finance", 1_075_000.0),
        ),
        organization_id="org-123",
        period="2026-Q2",
        generated_at=datetime(2026, 7, 13, tzinfo=UTC),
    )


def test_orchestrator_executes_full_pipeline() -> None:
    mock = _MockOllama('{"content": "ملخص تنفيذي"}')
    conversations = ConversationService()
    orchestrator = AiOrchestrator(
        ollama_client=mock,
        conversation_service=conversations,
    )

    result = orchestrator.execute(
        AiExecutionRequest(
            engine_id="waste",
            engine_input=_waste_input(),
            task=PromptTask.EXECUTIVE_SUMMARY,
            domain="waste",
        )
    )

    assert result.facts_contract.engine_id == "waste"
    assert result.prompt_context.selected_fact_count > 0
    assert result.composed_prompt.task is PromptTask.EXECUTIVE_SUMMARY
    assert result.parsed_response.format == "json"
    assert mock.messages[0]["role"] == "system"
    assert mock.messages[-1]["role"] == "user"
    assert len(conversations.get(result.conversation_id).turns) == 2


def test_orchestrator_reuses_conversation_for_multi_turn() -> None:
    mock = _MockOllama("second response")
    conversations = ConversationService()
    orchestrator = AiOrchestrator(
        ollama_client=mock,
        conversation_service=conversations,
    )

    first = orchestrator.execute(
        AiExecutionRequest(
            engine_id="waste",
            engine_input=_waste_input(),
            task=PromptTask.EXECUTIVE_SUMMARY,
            domain="waste",
        )
    )
    mock.response = "follow-up response"
    second = orchestrator.execute(
        AiExecutionRequest(
            engine_id="waste",
            engine_input=_waste_input(),
            task=PromptTask.EXECUTIVE_SUMMARY,
            domain="waste",
            conversation_id=first.conversation_id,
        )
    )

    assert second.conversation_id == first.conversation_id
    assert len(conversations.get(first.conversation_id).turns) == 4
    assert len(mock.messages) == 4  # system + 2 history + user
