"""Platform Default Notification Preferences gate helpers."""

from __future__ import annotations

from app.settings.models import ResolvedConfiguration


def is_notification_materialization_enabled(
    resolved: ResolvedConfiguration,
    notification_kind: str,
) -> bool:
    """Return whether a Platform Event kind may materialize a notification."""
    prefs = resolved.platform_default_notification_preferences
    if not prefs.notifications_enabled:
        return False
    return notification_kind in prefs.enabled_notification_kinds
