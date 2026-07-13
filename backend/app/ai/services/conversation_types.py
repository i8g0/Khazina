"""Conversation service types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4


ConversationRole = Literal["user", "assistant", "system"]


@dataclass(frozen=True, slots=True)
class ConversationTurn:
    role: ConversationRole
    content: str
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    id: str
    turns: list[ConversationTurn] = field(default_factory=list)
    engine_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


def new_conversation_id() -> str:
    return str(uuid4())
