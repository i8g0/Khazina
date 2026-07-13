"""Context Builder — consumes Facts Contract, produces Prompt Context."""

from app.ai.context.adapter import fact_to_prompt_fact
from app.ai.context.builder import ContextBuilder
from app.ai.context.types import ContextBuildOptions, PromptContext

__all__ = [
    "ContextBuilder",
    "ContextBuildOptions",
    "PromptContext",
    "fact_to_prompt_fact",
]
