"""User domain service: organization-scoped user lifecycle."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models import User
from app.db.models.enums import UserRole
from app.repositories import OrganizationRepository, UserRepository
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    DuplicateResourceError,
    InvalidStateError,
    ResourceNotFoundError,
)


class UserService(BaseService):
    """Business use cases for organization users.

    Passwords are hashed before persistence; authentication endpoints are
    introduced in a later sprint.
    """

    def __init__(
        self,
        session: Session,
        user_repository: UserRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        super().__init__(session)
        self._users = user_repository
        self._organizations = organization_repository

    def create_user(
        self,
        organization_id: uuid.UUID,
        *,
        full_name: str,
        email: str,
        password: str,
        role: UserRole | str,
    ) -> User:
        self._require_organization(organization_id)
        full_name = full_name.strip()
        email = self._normalize_email(email)
        if not full_name:
            raise BusinessValidationError("Full name must not be empty")
        if not password:
            raise BusinessValidationError("Password must not be empty")
        role_value = self._normalize_role(role)
        if self._users.get_by_email(email) is not None:
            raise DuplicateResourceError(f"User with email '{email}' already exists")

        user = User(
            organization_id=organization_id,
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role=role_value,
        )
        with self._transaction():
            self._users.create(user)
        return user

    def get_user(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> User:
        user = self._found(self._users.get_by_id(user_id), "User", user_id)
        self._check_ownership(user, "User", organization_id)
        return user

    def list_users(
        self,
        organization_id: uuid.UUID,
        *,
        active_only: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[User]:
        self._require_organization(organization_id)
        return self._users.list_for_organization(
            organization_id, active_only=active_only, limit=limit, offset=offset
        )

    def update_user(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        *,
        full_name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        role: UserRole | str | None = None,
    ) -> User:
        user = self.get_user(organization_id, user_id)
        if not user.is_active:
            raise InvalidStateError("Cannot update an inactive user")

        values: dict[str, object] = {}
        if full_name is not None:
            full_name = full_name.strip()
            if not full_name:
                raise BusinessValidationError("Full name must not be empty")
            values["full_name"] = full_name
        if email is not None:
            email = self._normalize_email(email)
            if email != user.email:
                existing = self._users.get_by_email(email)
                if existing is not None and existing.id != user.id:
                    raise DuplicateResourceError(
                        f"User with email '{email}' already exists"
                    )
                values["email"] = email
        if password is not None:
            if not password:
                raise BusinessValidationError("Password must not be empty")
            values["password_hash"] = hash_password(password)
        if role is not None:
            values["role"] = self._normalize_role(role)
        if not values:
            return user

        with self._transaction():
            self._users.update(user, values)
        return user

    def deactivate_user(
        self, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> User:
        user = self.get_user(organization_id, user_id)
        if not user.is_active:
            raise InvalidStateError("User is already inactive")
        with self._transaction():
            self._users.deactivate(user)
        return user

    # -- internals -------------------------------------------------------------

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _normalize_role(role: UserRole | str) -> str:
        if isinstance(role, UserRole):
            return role.value
        role_value = role.strip().lower()
        try:
            return UserRole(role_value).value
        except ValueError as exc:
            allowed = ", ".join(r.value for r in UserRole)
            raise BusinessValidationError(
                f"Invalid role '{role}'. Allowed values: {allowed}"
            ) from exc
