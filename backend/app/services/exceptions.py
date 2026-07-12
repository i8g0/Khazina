"""Service-layer (business) exceptions.

These exceptions describe business outcomes only. They carry no HTTP
semantics; translation to status codes and response shapes belongs to the
API layer (Sprint 3.7). Services translate repository exceptions
(``app.repositories.exceptions``) into these business-level errors.
"""

from __future__ import annotations

import uuid


class ServiceError(Exception):
    """Base class for all business-level service errors."""


class BusinessValidationError(ServiceError):
    """Input or workflow data violates a business rule (bad values, missing fields)."""


class ResourceNotFoundError(ServiceError):
    """A required business entity does not exist."""

    def __init__(self, entity_name: str, entity_id: uuid.UUID | str) -> None:
        super().__init__(f"{entity_name} with id '{entity_id}' was not found")
        self.entity_name = entity_name
        self.entity_id = entity_id


class DuplicateResourceError(ServiceError):
    """The operation would create a duplicate of an entity that must be unique."""


class OwnershipViolationError(ServiceError):
    """The referenced entity does not belong to the acting organization."""


class InvalidStateError(ServiceError):
    """The entity is in a state that does not permit the requested operation."""


class InvalidStateTransitionError(InvalidStateError):
    """The requested lifecycle transition is not allowed from the current state."""

    def __init__(
        self, entity_name: str, current_state: str, requested_state: str
    ) -> None:
        super().__init__(
            f"{entity_name} cannot transition from '{current_state}' "
            f"to '{requested_state}'"
        )
        self.entity_name = entity_name
        self.current_state = current_state
        self.requested_state = requested_state


class BusinessRuleViolationError(ServiceError):
    """A database integrity rule rejected the operation (unique/check/FK constraint)."""
