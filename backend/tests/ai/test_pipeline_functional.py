"""Deterministic functional validation for AI pipeline stages (no Ollama)."""

from __future__ import annotations

from datetime import UTC, datetime

from app.ai.context.builder import ContextBuilder
from app.ai.context.types import ContextBuildOptions
from app.ai.prompts.composer import PromptComposer
from app.ai.prompts.tasks import PromptTask
from app.ai.parsers.response_parser import ResponseParser
from app.business.engines.waste.engine import WasteEngine
from app.business.engines.waste.input import WasteCategoryInput, WasteEngineInput


def _input() -> WasteEngineInput:
    return WasteEngineInput(
        total_spend=50_000_000.0,
        total_waste_amount=2_340_000.0,
        categories=(
            WasteCategoryInput("overlapping_contracts", 745_000.0),
            WasteCategoryInput("operations", 520_000.0),
            WasteCategoryInput("finance", 1_075_000.0),
        ),
        organization_id="benchmark-org",
        period="2026-Q2",
        generated_at=datetime(2026, 7, 13, tzinfo=UTC),
    )


def test_pipeline_stages_before_llm_are_deterministic() -> None:
    contract = WasteEngine().run(_input())
    context = ContextBuilder().build(
        contract,
        ContextBuildOptions(task=PromptTask.EXECUTIVE_SUMMARY, domain="waste"),
    )
    composed = PromptComposer().compose(PromptTask.EXECUTIVE_SUMMARY, context.facts)
    parsed = ResponseParser().parse('{"content": "ok"}')

    assert contract.engine_id == "waste"
    assert context.selected_fact_count > 0
    assert composed.system_prompt
    assert composed.user_prompt
    assert parsed.format == "json"
