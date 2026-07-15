"""User notification preferences data access."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.db.models.user_notification_preferences import UserNotificationPreferences
from app.repositories.base import BaseRepository


class UserNotificationPreferencesRepository(BaseRepository):
    """Persistence for per-user notification preference documents."""

    def get_by_user(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> UserNotificationPreferences | None:
        stmt = select(UserNotificationPreferences).where(
            UserNotificationPreferences.organization_id == organization_id,
            UserNotificationPreferences.user_id == user_id,
        )
        return self._session.scalars(stmt).first()

    def create(
        self, record: UserNotificationPreferences
    ) -> UserNotificationPreferences:
        return self._add(record)

    def update(
        self,
        record: UserNotificationPreferences,
        values: dict[str, object],
    ) -> UserNotificationPreferences:
        return self._update(record, values)
