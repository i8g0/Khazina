"""Repository-layer exceptions.

Pure infrastructure/domain exceptions with no HTTP semantics. Translation to
HTTP responses (status codes, ApiResponse shapes) is the responsibility of
upper layers (exception handlers / API), not the repositories.
"""

import uuid


class RepositoryError(Exception):
    """Base class for repository-layer errors."""


class EntityNotFoundError(RepositoryError):
    """Raised when a required database entity does not exist."""

    def __init__(self, entity_name: str, entity_id: uuid.UUID) -> None:
        super().__init__(f"{entity_name} with id '{entity_id}' was not found")
        self.entity_name = entity_name
        self.entity_id = entity_id
