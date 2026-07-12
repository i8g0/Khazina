"""Shared service infrastructure.

Services own transaction boundaries: repositories only flush, and every
mutating service method finishes its unit of work through ``_transaction``,
which commits on success and rolls back on any failure. Database integrity
violations surfacing at commit time are translated into business-level
exceptions so upper layers never handle SQLAlchemy errors directly.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.services.exceptions import (
    BusinessRuleViolationError,
    OwnershipViolationError,
    ResourceNotFoundError,
)


class BaseService:
    """Session holder with transaction and validation helpers shared by all services."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @contextmanager
    def _transaction(self) -> Iterator[None]:
        """Unit-of-work boundary: commit on success, rollback on any error."""
        try:
            yield
        except Exception:
            self._session.rollback()
            raise
        self._commit()

    def _commit(self) -> None:
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise BusinessRuleViolationError(
                "The operation violates a data integrity rule "
                f"({exc.orig})"
            ) from exc

    # -- validation helpers -------------------------------------------------

    @staticmethod
    def _found(instance, entity_name: str, entity_id: uuid.UUID):
        """Translate a missing lookup into a business-level not-found error."""
        if instance is None:
            raise ResourceNotFoundError(entity_name, entity_id)
        return instance

    @staticmethod
    def _check_ownership(
        entity, entity_name: str, organization_id: uuid.UUID
    ) -> None:
        """Ensure the entity belongs to the acting organization."""
        if entity.organization_id != organization_id:
            raise OwnershipViolationError(
                f"{entity_name} '{entity.id}' does not belong to "
                f"organization '{organization_id}'"
            )
