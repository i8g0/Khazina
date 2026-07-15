"""User notification preference document shapes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.notifications.constants import USER_PREFERENCES_VERSION


@dataclass(frozen=True, slots=True)
class ResolvedUserNotificationPreferences:
    notifications_enabled: bool
    muted_notification_kinds: frozenset[str]
    preferences_version: str

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "notifications_enabled": self.notifications_enabled,
            "muted_notification_kinds": sorted(self.muted_notification_kinds),
            "preferences_version": self.preferences_version,
        }


@dataclass(slots=True)
class PersistedUserNotificationPreferences:
    notifications_enabled: bool = True
    muted_notification_kinds: set[str] = field(default_factory=set)

    @classmethod
    def from_dict(
        cls, data: dict[str, Any] | None
    ) -> PersistedUserNotificationPreferences:
        if not data:
            return cls()
        muted = data.get("muted_notification_kinds") or []
        return cls(
            notifications_enabled=bool(data.get("notifications_enabled", True)),
            muted_notification_kinds={str(item) for item in muted},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "notifications_enabled": self.notifications_enabled,
            "muted_notification_kinds": sorted(self.muted_notification_kinds),
            "preferences_version": USER_PREFERENCES_VERSION,
        }
