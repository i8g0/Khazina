"""Shared repository infrastructure.

Repositories receive an externally managed SQLAlchemy ``Session`` (dependency
injection compatible with ``app.db.session.get_db``) and never create sessions,
commit, or roll back. Writes are flushed so server defaults (UUIDs, timestamps)
are populated on returned instances; transaction boundaries belong to the
caller (Service Layer, Sprint 3.6).
"""

from __future__ import annotations

import uuid
from typing import Any, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories.exceptions import EntityNotFoundError

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository:
    """Session holder with generic persistence helpers shared by all domain repositories."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # -- generic helpers -------------------------------------------------

    def _get(self, model: type[ModelT], entity_id: uuid.UUID) -> ModelT | None:
        return self._session.get(model, entity_id)

    def _require(self, model: type[ModelT], entity_id: uuid.UUID) -> ModelT:
        instance = self._session.get(model, entity_id)
        if instance is None:
            raise EntityNotFoundError(model.__name__, entity_id)
        return instance

    def _add(self, instance: ModelT) -> ModelT:
        self._session.add(instance)
        self._session.flush()
        return instance

    def _add_all(self, instances: list[ModelT]) -> list[ModelT]:
        self._session.add_all(instances)
        self._session.flush()
        return instances

    def _update(self, instance: ModelT, values: dict[str, Any]) -> ModelT:
        for field, value in values.items():
            setattr(instance, field, value)
        self._session.flush()
        return instance

    def _delete(self, instance: Base) -> None:
        self._session.delete(instance)
        self._session.flush()

    def _list(self, stmt: Select[tuple[ModelT]]) -> list[ModelT]:
        return list(self._session.scalars(stmt).all())

    def _count(self, stmt: Select[tuple[ModelT]]) -> int:
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        return self._session.scalar(count_stmt) or 0

    @staticmethod
    def _paginate(
        stmt: Select[tuple[ModelT]],
        limit: int | None = None,
        offset: int | None = None,
    ) -> Select[tuple[ModelT]]:
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        return stmt
