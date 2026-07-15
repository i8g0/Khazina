"""User notification preferences service."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.user_notification_preferences import UserNotificationPreferences
from app.notifications.models import (
    PersistedUserNotificationPreferences,
    ResolvedUserNotificationPreferences,
)
from app.notifications.user_preferences_resolver import (
    merge_user_preferences_patch,
    resolve_user_notification_preferences,
    validate_user_preferences_patch,
)
from app.repositories import (
    OrganizationRepository,
    UserNotificationPreferencesRepository,
    UserRepository,
)
from app.services.base import BaseService
from app.services.exceptions import OwnershipViolationError, ResourceNotFoundError
from app.settings.service import SettingsService


class UserNotificationPreferencesService(BaseService):
    """Per-user notification preference persistence and resolution."""

    def __init__(
        self,
        session: Session,
        preferences_repository: UserNotificationPreferencesRepository,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
        settings_service: SettingsService,
    ) -> None:
        super().__init__(session)
        self._preferences = preferences_repository
        self._organizations = organization_repository
        self._users = user_repository
        self._settings = settings_service

    def get_preferences(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ResolvedUserNotificationPreferences:
        self._require_membership(organization_id, user_id)
        persisted = self._load_or_initialize(organization_id, user_id)
        return resolve_user_notification_preferences(persisted)

    def patch_preferences(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        patch: dict[str, Any],
    ) -> ResolvedUserNotificationPreferences:
        self._require_membership(organization_id, user_id)
        resolved_org = self._settings.get_resolved_settings(organization_id)
        validate_user_preferences_patch(
            patch,
            org_enabled_kinds=(
                resolved_org.platform_default_notification_preferences.enabled_notification_kinds
            ),
        )
        current = self._load_or_initialize(organization_id, user_id)
        merged = merge_user_preferences_patch(current, patch)
        record = self._preferences.get_by_user(organization_id, user_id)
        payload = merged.to_dict()
        with self._transaction():
            if record is None:
                record = UserNotificationPreferences(
                    organization_id=organization_id,
                    user_id=user_id,
                    preferences_document=payload,
                )
                self._preferences.create(record)
            else:
                self._preferences.update(
                    record, {"preferences_document": payload}
                )
        return resolve_user_notification_preferences(merged)

    def get_persisted_for_user(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ResolvedUserNotificationPreferences | None:
        record = self._preferences.get_by_user(organization_id, user_id)
        if record is None:
            return None
        return resolve_user_notification_preferences(
            PersistedUserNotificationPreferences.from_dict(
                record.preferences_document
            )
        )

    def _load_or_initialize(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> PersistedUserNotificationPreferences:
        record = self._preferences.get_by_user(organization_id, user_id)
        if record is None:
            return PersistedUserNotificationPreferences()
        return PersistedUserNotificationPreferences.from_dict(
            record.preferences_document
        )

    def _require_membership(
        self, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
        user = self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise ResourceNotFoundError("User", user_id)
        if user.organization_id != organization_id:
            raise OwnershipViolationError(
                f"User '{user_id}' does not belong to organization '{organization_id}'"
            )
