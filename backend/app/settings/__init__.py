"""Organization settings module (Sprint 6.8)."""

from app.settings.constants import DEFAULT_ENABLED_NOTIFICATION_KINDS
from app.settings.models import ResolvedConfiguration
from app.settings.notification_gates import is_notification_materialization_enabled

__all__ = [
    "DEFAULT_ENABLED_NOTIFICATION_KINDS",
    "ResolvedConfiguration",
    "SettingsService",
    "is_notification_materialization_enabled",
]


def __getattr__(name: str):
    if name == "SettingsService":
        from app.settings.service import SettingsService

        return SettingsService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
