"""Notifications module (Sprint 6.7)."""

from app.notifications.constants import ALL_PLATFORM_EVENT_KINDS

__all__ = [
    "ALL_PLATFORM_EVENT_KINDS",
    "MaterializedNotification",
    "NotificationBuilder",
    "NotificationService",
    "NotificationView",
]


def __getattr__(name: str):
    if name == "NotificationBuilder":
        from app.notifications.builder import NotificationBuilder

        return NotificationBuilder
    if name == "MaterializedNotification":
        from app.notifications.builder import MaterializedNotification

        return MaterializedNotification
    if name == "NotificationService":
        from app.notifications.service import NotificationService

        return NotificationService
    if name == "NotificationView":
        from app.notifications.service import NotificationView

        return NotificationView
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
