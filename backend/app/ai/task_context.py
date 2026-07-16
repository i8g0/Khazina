"""Current AI task context for provider telemetry (parallel-safe)."""

from __future__ import annotations

import contextvars

_current_ai_task: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_ai_task",
    default=None,
)


def set_current_ai_task(task: str | None) -> contextvars.Token[str | None]:
    return _current_ai_task.set(task)


def reset_current_ai_task(token: contextvars.Token[str | None]) -> None:
    _current_ai_task.reset(token)


def get_current_ai_task() -> str | None:
    return _current_ai_task.get()
