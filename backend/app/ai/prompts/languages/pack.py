"""Language pack definitions for the Prompt Engine."""

from __future__ import annotations

from dataclasses import dataclass

from app.ai.prompts.tasks import PromptTask


@dataclass(frozen=True, slots=True)
class LanguagePack:
    """Localized prompt content for a single language."""

    code: str
    system_prompt: str
    output_rules: str
    facts_header: str
    no_facts_message: str
    label_unit: str
    label_severity: str
    label_confidence: str
    label_source: str
    task_templates: dict[PromptTask, str]
