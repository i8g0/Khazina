"""Context Builder — selects and orders facts from a Facts Contract."""

from __future__ import annotations

from app.ai.context.adapter import fact_to_prompt_fact
from app.ai.context.types import ContextBuildOptions, PromptContext
from app.ai.prompts.tasks import PromptTask
from app.business.facts.contract import Fact, FactsContract

_SEVERITY_RANK = {
    "high": 0,
    "medium": 1,
    "low": 2,
}


def _severity_rank(fact: Fact) -> tuple[int, str, str]:
    rank = _SEVERITY_RANK.get((fact.severity or "").lower(), 3)
    return (rank, fact.metric, fact.value)


class ContextBuilder:
    """Filters and orders Facts Contract records into Prompt Context."""

    def build(
        self,
        contract: FactsContract,
        options: ContextBuildOptions,
    ) -> PromptContext:
        facts = list(contract.facts)
        if options.domain is not None:
            facts = [fact for fact in facts if fact.domain == options.domain]

        facts = self._prioritize_for_task(facts, options.task)
        ordered = sorted(facts, key=_severity_rank)

        if options.max_facts is not None and options.max_facts >= 0:
            ordered = ordered[: options.max_facts]

        prompt_facts = tuple(fact_to_prompt_fact(fact) for fact in ordered)
        return PromptContext(
            task=options.task,
            facts=prompt_facts,
            engine_id=contract.engine_id,
            contract_version=contract.contract_version,
            total_fact_count=len(contract.facts),
            selected_fact_count=len(prompt_facts),
            extensions=dict(options.extensions),
        )

    @staticmethod
    def _prioritize_for_task(facts: list[Fact], task: PromptTask) -> list[Fact]:
        """Task-aware selection without calculations — severity-bearing facts first."""
        if not facts:
            return facts
        if task in {PromptTask.RISK_ANALYSIS, PromptTask.RECOMMENDATIONS}:
            prioritized = [fact for fact in facts if fact.severity]
            remainder = [fact for fact in facts if not fact.severity]
            return prioritized + remainder
        return facts
