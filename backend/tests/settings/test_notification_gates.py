"""Platform Default Notification Preferences gate tests."""

from __future__ import annotations

import uuid

from app.db.models import Organization
from app.settings.constants import NOTIFICATION_KIND_REPORT_GENERATED
from app.settings.models import PersistedSettingsDocument
from app.settings.notification_gates import is_notification_materialization_enabled
from app.settings.resolver import resolve_configuration


def _resolved(**overrides: object):
    org = Organization(name="Org", platform_name="خزينة")
    org.id = uuid.uuid4()
    org.is_active = True
    notification = overrides.get("notification", {})
    persisted = PersistedSettingsDocument(
        platform_default_notification_preferences=dict(notification)  # type: ignore[arg-type]
    )
    return resolve_configuration(org, persisted)


def test_master_switch_disables_all_kinds() -> None:
    resolved = _resolved(notification={"notifications_enabled": False})
    assert not is_notification_materialization_enabled(
        resolved, NOTIFICATION_KIND_REPORT_GENERATED
    )


def test_disabled_kind_skipped() -> None:
    resolved = _resolved(notification={"enabled_notification_kinds": []})
    assert not is_notification_materialization_enabled(
        resolved, NOTIFICATION_KIND_REPORT_GENERATED
    )


def test_enabled_kind_allowed() -> None:
    resolved = _resolved()
    assert is_notification_materialization_enabled(
        resolved, NOTIFICATION_KIND_REPORT_GENERATED
    )
