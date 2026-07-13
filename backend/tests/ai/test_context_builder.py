"""Context Builder unit tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.ai.context.builder import ContextBuilder
from app.ai.context.types import ContextBuildOptions
from app.ai.prompts.tasks import PromptTask
from app.business.facts.contract import Fact, FactsContract


def _contract(*facts: Fact) -> FactsContract:
    return FactsContract(
        contract_version="1.0",
        engine_id="waste",
        engine_version="1.0.0",
        generated_at=datetime(2026, 7, 13, tzinfo=UTC),
        facts=facts,
    )


def test_context_builder_filters_domain_and_orders_by_severity() -> None:
    contract = _contract(
        Fact("waste", "waste.percentage", "4.68", "waste:analysis", severity="low"),
        Fact("waste", "waste.overall_level", "low", "waste:analysis", severity="low"),
        Fact("risk", "risk.score", "7", "risk:analysis", severity="high"),
        Fact("waste", "waste.total_amount", "2340000.00", "waste:analysis", severity="high"),
    )
    context = ContextBuilder().build(
        contract,
        ContextBuildOptions(task=PromptTask.EXECUTIVE_SUMMARY, domain="waste"),
    )

    assert context.selected_fact_count == 3
    assert context.facts[0].severity == "high"
    assert all(fact.domain == "waste" for fact in context.facts)


def test_context_builder_is_deterministic() -> None:
    contract = _contract(
        Fact("waste", "b.metric", "1", "src", severity="medium"),
        Fact("waste", "a.metric", "2", "src", severity="high"),
    )
    builder = ContextBuilder()
    options = ContextBuildOptions(task=PromptTask.EXECUTIVE_SUMMARY)

    first = builder.build(contract, options)
    second = builder.build(contract, options)
    assert first.facts == second.facts


def test_context_builder_respects_max_facts() -> None:
    contract = _contract(
        Fact("waste", "one", "1", "src"),
        Fact("waste", "two", "2", "src"),
        Fact("waste", "three", "3", "src"),
    )
    context = ContextBuilder().build(
        contract,
        ContextBuildOptions(task=PromptTask.EXECUTIVE_SUMMARY, max_facts=2),
    )
    assert context.selected_fact_count == 2
