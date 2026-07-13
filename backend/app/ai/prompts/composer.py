"""Prompt composition — assembles system prompt, template, and facts."""

from __future__ import annotations

from collections.abc import Sequence

from app.ai.prompts.builder import build_user_prompt
from app.ai.prompts.facts import PromptFact
from app.ai.prompts.language_config import get_default_prompt_language
from app.ai.prompts.metadata import PromptMetadata, build_prompt_metadata
from app.ai.prompts.system import build_system_prompt
from app.ai.prompts.tasks import PromptTask
from app.ai.prompts.templates import get_task_template


class ComposedPrompt:
    """Complete prompt package ready for LLM invocation."""

    __slots__ = (
        "task",
        "system_prompt",
        "task_instructions",
        "facts_prompt",
        "metadata",
    )

    def __init__(
        self,
        *,
        task: PromptTask,
        system_prompt: str,
        task_instructions: str,
        facts_prompt: str,
        metadata: PromptMetadata,
    ) -> None:
        self.task = task
        self.system_prompt = system_prompt
        self.task_instructions = task_instructions
        self.facts_prompt = facts_prompt
        self.metadata = metadata

    @property
    def prompt_version(self) -> str:
        return self.metadata.prompt_version

    @property
    def prompt_language(self) -> str:
        return self.metadata.prompt_language

    @property
    def created_at(self):
        return self.metadata.created_at

    @property
    def user_prompt(self) -> str:
        """Task template plus formatted facts — the user/message role content."""
        return f"{self.task_instructions.rstrip()}\n\n{self.facts_prompt.rstrip()}\n"

    @property
    def final_prompt(self) -> str:
        """Single combined prompt string for callers that use one message block."""
        return (
            f"{self.system_prompt.rstrip()}\n\n"
            f"{self.user_prompt.rstrip()}\n"
        )


class PromptComposer:
    """Assembles system prompt, task template, and prepared facts."""

    def compose(
        self,
        task: PromptTask,
        facts: Sequence[PromptFact],
        *,
        prompt_language: str | None = None,
    ) -> ComposedPrompt:
        language = prompt_language or get_default_prompt_language()
        metadata = build_prompt_metadata(task=task, prompt_language=language)
        return ComposedPrompt(
            task=task,
            system_prompt=build_system_prompt(prompt_language=language),
            task_instructions=get_task_template(task, prompt_language=language),
            facts_prompt=build_user_prompt(facts, prompt_language=language),
            metadata=metadata,
        )


def compose_prompt(
    task: PromptTask,
    facts: Sequence[PromptFact],
    *,
    prompt_language: str | None = None,
) -> ComposedPrompt:
    """Compose a production-ready prompt package (public Prompt Engine entry point)."""
    return PromptComposer().compose(
        task=task,
        facts=facts,
        prompt_language=prompt_language,
    )
