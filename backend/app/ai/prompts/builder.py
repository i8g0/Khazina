"""User prompt builder — formats prepared facts for the LLM."""

from __future__ import annotations

from collections.abc import Sequence

from app.ai.prompts.facts import PromptFact
from app.ai.prompts.language_config import get_default_prompt_language
from app.ai.prompts.languages import get_language_pack
from app.ai.prompts.languages.pack import LanguagePack
from app.presentation.metric_labels import build_evidence_blocks, format_fact_for_prompt

_FACT_SORT_KEY = lambda fact: (fact.domain, fact.metric, fact.value, fact.source or "")


def build_user_prompt(
    facts: Sequence[PromptFact],
    *,
    prompt_language: str | None = None,
) -> str:
    """Transform prepared prompt facts into executive evidence blocks."""
    language = prompt_language or get_default_prompt_language()
    pack = get_language_pack(language)

    if not facts:
        return pack.facts_header + pack.no_facts_message

    if any(fact.domain == "waste" for fact in facts):
        rendered = build_evidence_blocks(facts, pack)
        return f"{pack.facts_header}{rendered}"

    ordered = sorted(facts, key=_FACT_SORT_KEY)
    rendered = "\n".join(format_fact_for_prompt(fact, pack) for fact in ordered)
    return f"{pack.facts_header}{rendered}\n"
