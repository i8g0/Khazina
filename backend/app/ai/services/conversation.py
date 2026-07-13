"""In-memory conversation state management."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.ai.exceptions import ConversationNotFoundError
from app.ai.services.conversation_types import (
    Conversation,
    ConversationRole,
    ConversationTurn,
    new_conversation_id,
)


class ConversationService:
    """Lightweight in-memory conversation store — no database persistence."""

    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}

    def create(
        self,
        *,
        engine_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Conversation:
        conversation = Conversation(
            id=new_conversation_id(),
            engine_id=engine_id,
            metadata=dict(metadata or {}),
        )
        self._conversations[conversation.id] = conversation
        return conversation

    def get(self, conversation_id: str) -> Conversation:
        try:
            return self._conversations[conversation_id]
        except KeyError as exc:
            raise ConversationNotFoundError(
                f"Conversation not found: {conversation_id}"
            ) from exc

    def get_or_create(
        self,
        conversation_id: str | None,
        *,
        engine_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Conversation:
        if conversation_id is None:
            return self.create(engine_id=engine_id, metadata=metadata)
        return self.get(conversation_id)

    def append_turn(
        self,
        conversation_id: str,
        *,
        role: ConversationRole,
        content: str,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> ConversationTurn:
        conversation = self.get(conversation_id)
        turn = ConversationTurn(
            role=role,
            content=content,
            created_at=created_at or datetime.now(UTC),
            metadata=dict(metadata or {}),
        )
        conversation.turns.append(turn)
        conversation.updated_at = turn.created_at
        if metadata and metadata.get("engine_id"):
            conversation.engine_id = str(metadata["engine_id"])
        return turn

    def history_messages(self, conversation_id: str) -> list[dict[str, str]]:
        """Return prior turns formatted for LLM chat APIs."""
        conversation = self.get(conversation_id)
        return [
            {"role": turn.role, "content": turn.content}
            for turn in conversation.turns
            if turn.role in {"user", "assistant", "system"}
        ]

    def clear(self) -> None:
        """Remove all conversations — for tests only."""
        self._conversations.clear()
