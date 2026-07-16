"""BaseRepository helper tests (Sprint 8.1)."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.repositories.base import BaseRepository
from app.repositories.exceptions import EntityNotFoundError


class _Repo(BaseRepository):
    pass


def test_require_raises_entity_not_found_when_missing() -> None:
    session = MagicMock()
    session.get.return_value = None
    repo = _Repo(session)
    entity_id = uuid.uuid4()

    with pytest.raises(EntityNotFoundError) as exc_info:
        repo._require(MagicMock, entity_id)

    assert exc_info.value.entity_id == entity_id


def test_add_flushes_new_instance() -> None:
    session = MagicMock()
    repo = _Repo(session)
    instance = MagicMock()

    result = repo._add(instance)

    session.add.assert_called_once_with(instance)
    session.flush.assert_called_once()
    assert result is instance


def test_delete_removes_instance() -> None:
    session = MagicMock()
    repo = _Repo(session)
    instance = MagicMock()

    repo._delete(instance)

    session.delete.assert_called_once_with(instance)
    session.flush.assert_called_once()
