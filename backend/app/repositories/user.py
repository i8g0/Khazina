from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.db.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Data access for the User domain."""

    def create(self, user: User) -> User:
        return self._add(user)

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._session.scalars(stmt).first()

    def list_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        active_only: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[User]:
        stmt = select(User).where(User.organization_id == organization_id)
        if active_only:
            stmt = stmt.where(User.is_active.is_(True))
        stmt = self._paginate(
            stmt.order_by(User.full_name, User.email), limit, offset
        )
        return self._list(stmt)

    def update(self, user: User, values: dict[str, Any]) -> User:
        return self._update(user, values)

    def deactivate(self, user: User) -> User:
        return self._update(user, {"is_active": False})
