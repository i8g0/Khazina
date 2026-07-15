"""Effective notification preference resolution (Sprint 6.9)."""

from __future__ import annotations

from typing import Any


def is_effective_notification_materialization_enabled(
    resolved: Any,
    user_prefs: Any | None,
    notification_kind: str,
) -> bool:
    """Merge org Platform Default Notification Preferences with user overrides."""
    org_prefs = resolved.platform_default_notification_preferences
    if not org_prefs.notifications_enabled:
        return False
    if notification_kind not in org_prefs.enabled_notification_kinds:
        return False
    if user_prefs is None:
        return True
    if not user_prefs.notifications_enabled:
        return False
    if notification_kind in user_prefs.muted_notification_kinds:
        return False
    return True
