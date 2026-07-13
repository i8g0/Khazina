"""Conversation Service unit tests."""

from __future__ import annotations

import pytest

from app.ai.exceptions import ConversationNotFoundError
from app.ai.services.conversation import ConversationService


def test_conversation_service_create_and_append_turns() -> None:
    service = ConversationService()
    conversation = service.create(engine_id="waste")

    service.append_turn(conversation.id, role="user", content="first question")
    service.append_turn(conversation.id, role="assistant", content="first answer")

    stored = service.get(conversation.id)
    assert len(stored.turns) == 2
    assert stored.engine_id == "waste"
    assert service.history_messages(conversation.id)[0]["role"] == "user"


def test_conversation_service_multi_turn_history() -> None:
    service = ConversationService()
    conversation = service.create()
    service.append_turn(conversation.id, role="user", content="turn-1")
    service.append_turn(conversation.id, role="assistant", content="reply-1")
    service.append_turn(conversation.id, role="user", content="turn-2")

    history = service.history_messages(conversation.id)
    assert [item["content"] for item in history] == ["turn-1", "reply-1", "turn-2"]


def test_conversation_service_missing_id_raises() -> None:
    service = ConversationService()
    with pytest.raises(ConversationNotFoundError):
        service.get("missing-id")
