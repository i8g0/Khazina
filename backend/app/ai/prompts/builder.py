"""User prompt builder — formats prepared facts for the LLM."""

from __future__ import annotations

from collections.abc import Sequence

from app.ai.prompts.facts import PromptFact
from app.ai.prompts.language_config import get_default_prompt_language
from app.ai.prompts.languages import get_language_pack
from app.ai.prompts.languages.pack import LanguagePack

_FACT_SORT_KEY = lambda fact: (fact.domain, fact.metric, fact.value, fact.source or "")


def _format_fact(fact: PromptFact, pack: LanguagePack) -> str:
    lines = [
        f"- **{fact.domain}** / {fact.metric}: {fact.value}",
    ]
    if fact.unit:
        lines.append(f"  - {pack.label_unit}: {fact.unit}")
    if fact.severity:
        lines.append(f"  - {pack.label_severity}: {fact.severity}")
    if fact.confidence:
        lines.append(f"  - {pack.label_confidence}: {fact.confidence}")
    if fact.source:
        lines.append(f"  - {pack.label_source}: {fact.source}")
    return "\n".join(lines)


def build_user_prompt(
    facts: Sequence[PromptFact],
    *,
    prompt_language: str | None = None,
) -> str:
    """Transform prepared prompt facts into a readable user prompt section."""
    language = prompt_language or get_default_prompt_language()
    pack = get_language_pack(language)

    if not facts:
        return pack.facts_header + pack.no_facts_message

    ordered = sorted(facts, key=_FACT_SORT_KEY)
    rendered = "\n".join(_format_fact(fact, pack) for fact in ordered)
    return f"{pack.facts_header}{rendered}\n"
