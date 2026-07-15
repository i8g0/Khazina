"""User notification preferences service tests."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.notifications.constants import KIND_REPORT_GENERATED
from app.settings.constants import DEFAULT_ENABLED_NOTIFICATION_KINDS
from app.settings.exceptions import SettingsValidationError
from app.notifications.user_preferences_service import UserNotificationPreferencesService


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


def _service(org_id: uuid.UUID, user_id: uuid.UUID) -> UserNotificationPreferencesService:
    session = MagicMock()
    prefs_repo = MagicMock()
    prefs_repo.get_by_user.return_value = None
    prefs_repo.create.side_effect = lambda r: r
    org_repo = MagicMock()
    org_repo.get_organization.return_value = MagicMock()
    user = MagicMock()
    user.id = user_id
    user.organization_id = org_id
    user.is_active = True
    user_repo = MagicMock()
    user_repo.get_by_id.return_value = user
    settings = MagicMock()
    org_prefs = MagicMock()
    org_prefs.notifications_enabled = True
    org_prefs.enabled_notification_kinds = DEFAULT_ENABLED_NOTIFICATION_KINDS
    resolved = MagicMock()
    resolved.platform_default_notification_preferences = org_prefs
    settings.get_resolved_settings.return_value = resolved
    session.commit = MagicMock()
    session.rollback = MagicMock()
    return UserNotificationPreferencesService(
        session, prefs_repo, org_repo, user_repo, settings
    )


def test_get_preferences_lazy_defaults(org_id: uuid.UUID, user_id: uuid.UUID) -> None:
    service = _service(org_id, user_id)
    resolved = service.get_preferences(org_id, user_id)
    assert resolved.notifications_enabled is True
    assert resolved.muted_notification_kinds == frozenset()


def test_patch_mute_kind(org_id: uuid.UUID, user_id: uuid.UUID) -> None:
    service = _service(org_id, user_id)
    resolved = service.patch_preferences(
        org_id,
        user_id,
        {"muted_notification_kinds": [KIND_REPORT_GENERATED]},
    )
    assert KIND_REPORT_GENERATED in resolved.muted_notification_kinds


def test_patch_rejects_org_disabled_kind(org_id: uuid.UUID, user_id: uuid.UUID) -> None:
    service = _service(org_id, user_id)
    service._settings.get_resolved_settings.return_value.platform_default_notification_preferences.enabled_notification_kinds = frozenset()  # type: ignore[attr-defined]
    with pytest.raises(SettingsValidationError):
        service.patch_preferences(
            org_id,
            user_id,
            {"muted_notification_kinds": [KIND_REPORT_GENERATED]},
        )
