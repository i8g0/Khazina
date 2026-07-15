"""User notification preference API schemas."""

from __future__ import annotations

from pydantic import Field

from app.schemas.common import FullTimestampResponse, SchemaBase


class UserNotificationPreferencesResponse(SchemaBase):
    notifications_enabled: bool
    muted_notification_kinds: list[str]
    preferences_version: str


class UserNotificationPreferencesPatch(SchemaBase):
    notifications_enabled: bool | None = None
    muted_notification_kinds: list[str] | None = None
