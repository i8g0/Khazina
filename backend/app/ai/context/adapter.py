"""Map Facts Contract records to Prompt Engine input types."""

from __future__ import annotations

from app.ai.prompts.facts import PromptFact
from app.business.facts.contract import Fact


def fact_to_prompt_fact(fact: Fact) -> PromptFact:
    """Deterministic adapter — no transformation of values."""
    return PromptFact(
        domain=fact.domain,
        metric=fact.metric,
        value=fact.value,
        unit=fact.unit,
        severity=fact.severity,
        confidence=fact.confidence,
        source=fact.source,
    )
