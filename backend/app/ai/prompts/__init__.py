"""Prompt Engine — transforms structured facts into LLM prompts.

Public interface: ``compose_prompt``, ``PromptComposer``, ``PROMPT_VERSION``,
``get_default_prompt_language``, ``PromptMetadata``.
"""

from app.ai.prompts.composer import ComposedPrompt, PromptComposer, compose_prompt
from app.ai.prompts.facts import PromptFact
from app.ai.prompts.language_config import get_default_prompt_language
from app.ai.prompts.metadata import PromptMetadata, build_prompt_metadata
from app.ai.prompts.tasks import PromptTask
from app.ai.prompts.templates import iter_supported_tasks, supported_tasks
from app.ai.prompts.version import PROMPT_VERSION

__all__ = [
    "PROMPT_VERSION",
    "ComposedPrompt",
    "PromptComposer",
    "PromptFact",
    "PromptMetadata",
    "PromptTask",
    "build_prompt_metadata",
    "compose_prompt",
    "get_default_prompt_language",
    "iter_supported_tasks",
    "supported_tasks",
]
