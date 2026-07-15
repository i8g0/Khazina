"""Settings domain exceptions."""

from __future__ import annotations

from app.services.exceptions import BusinessValidationError, InvalidStateError


class SettingsValidationError(BusinessValidationError):
    """Persisted or patched settings violate schema or business bounds."""


class SettingsAccessError(InvalidStateError):
    """Settings cannot be accessed for the organization (e.g. inactive)."""


class AiRecommendationsDisabledError(InvalidStateError):
    """AI recommendations are disabled for this organization."""

    def __init__(self) -> None:
        super().__init__(
            "AI recommendations are disabled for this organization"
        )
