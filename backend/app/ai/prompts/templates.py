"""Task-specific prompt templates.

Task instructions and output rules are loaded from language packs — not
hardcoded in this module. One language per composed prompt.

Extending tasks
---------------
1. Add a new ``PromptTask`` member in ``tasks.py``.
2. Register its template body via ``register_task_template(task, body, language=...)``.
3. Export the task from ``app.ai.prompts`` if it becomes public.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.ai.prompts.language_config import get_default_prompt_language
from app.ai.prompts.languages import get_language_pack
from app.ai.prompts.languages.ar import ARABIC_PACK
from app.ai.prompts.tasks import PromptTask

_TASK_TEMPLATE_OVERRIDES: dict[tuple[str, PromptTask], str] = {}


def register_task_template(
    task: PromptTask,
    body: str,
    *,
    language: str | None = None,
) -> None:
    """Register or replace the instruction body for ``task`` in one language."""
    language_code = language or get_default_prompt_language()
    _TASK_TEMPLATE_OVERRIDES[(language_code, task)] = body


def supported_tasks(*, language: str | None = None) -> tuple[PromptTask, ...]:
    """Return all tasks that have templates for ``language``."""
    language_code = language or get_default_prompt_language()
    pack = get_language_pack(language_code)
    keys = set(pack.task_templates)
    keys.update(task for lang, task in _TASK_TEMPLATE_OVERRIDES if lang == language_code)
    return tuple(task for task in PromptTask if task in keys)


def iter_supported_tasks(*, language: str | None = None) -> Iterable[PromptTask]:
    """Iterate registered tasks for ``language`` in enum definition order."""
    available = set(supported_tasks(language=language))
    for task in PromptTask:
        if task in available:
            yield task


def _resolve_task_body(task: PromptTask, language_code: str) -> str:
    override = _TASK_TEMPLATE_OVERRIDES.get((language_code, task))
    if override is not None:
        return override
    pack = get_language_pack(language_code)
    try:
        return pack.task_templates[task]
    except KeyError as exc:
        raise KeyError(
            f"No template registered for task {task} in language {language_code}"
        ) from exc


def get_task_template(task: PromptTask, *, prompt_language: str | None = None) -> str:
    """Return task instructions and output rules for one language only."""
    language_code = prompt_language or get_default_prompt_language()
    body = _resolve_task_body(task, language_code)
    output_rules = get_language_pack(language_code).output_rules
    return f"{body.rstrip()}\n\n{output_rules.rstrip()}\n"


def _bootstrap_builtin_task_templates() -> None:
    for task, body in ARABIC_PACK.task_templates.items():
        _TASK_TEMPLATE_OVERRIDES.setdefault(("ar", task), body)


_bootstrap_builtin_task_templates()

__all__ = [
    "PromptTask",
    "get_task_template",
    "iter_supported_tasks",
    "register_task_template",
    "supported_tasks",
]
