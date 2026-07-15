"""User notification preferences resolver."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from app.notifications.constants import ALL_PLATFORM_EVENT_KINDS
from app.notifications.models import (
    PersistedUserNotificationPreferences,
    ResolvedUserNotificationPreferences,
)

if TYPE_CHECKING:
    from app.settings.exceptions import SettingsValidationError


def resolve_user_notification_preferences(
    persisted: PersistedUserNotificationPreferences,
) -> ResolvedUserNotificationPreferences:
    return ResolvedUserNotificationPreferences(
        notifications_enabled=persisted.notifications_enabled,
        muted_notification_kinds=frozenset(persisted.muted_notification_kinds),
        preferences_version=persisted.to_dict()["preferences_version"],
    )


def validate_user_preferences_patch(
    patch: dict[str, Any],
    *,
    org_enabled_kinds: frozenset[str],
) -> None:
    from app.settings.exceptions import SettingsValidationError

    if "notifications_enabled" in patch and not isinstance(
        patch["notifications_enabled"], bool
    ):
        raise SettingsValidationError("notifications_enabled must be a boolean")
    muted = patch.get("muted_notification_kinds")
    if muted is not None:
        if not isinstance(muted, list):
            raise SettingsValidationError(
                "muted_notification_kinds must be a list"
            )
        normalized = frozenset(str(item) for item in muted)
        unknown = normalized - ALL_PLATFORM_EVENT_KINDS
        if unknown:
            raise SettingsValidationError(
                f"Unknown notification kinds: {', '.join(sorted(unknown))}"
            )
        not_org_enabled = normalized - org_enabled_kinds
        if not_org_enabled:
            raise SettingsValidationError(
                "Cannot mute kinds that are disabled at organization level: "
                f"{', '.join(sorted(not_org_enabled))}"
            )


def merge_user_preferences_patch(
    current: PersistedUserNotificationPreferences,
    patch: dict[str, Any],
) -> PersistedUserNotificationPreferences:
    merged = PersistedUserNotificationPreferences(
        notifications_enabled=current.notifications_enabled,
        muted_notification_kinds=set(current.muted_notification_kinds),
    )
    if "notifications_enabled" in patch:
        merged.notifications_enabled = bool(patch["notifications_enabled"])
    if "muted_notification_kinds" in patch:
        merged.muted_notification_kinds = {
            str(item) for item in patch["muted_notification_kinds"]
        }
    return merged
