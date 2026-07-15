"""Organization settings API schemas."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from app.schemas.common import SchemaBase
from app.settings.constants import FORBIDDEN_SETTINGS_KEYS


class OrganizationIdentityResponse(SchemaBase):
    name: str
    platform_name: str
    executive_title: str | None


class OrganizationSettingsSectionResponse(SchemaBase):
    locale: str
    date_display_format: str
    currency_display_code: str


class LocalizationSectionResponse(SchemaBase):
    prompt_language: str
    report_language: str
    prompt_language_source: str
    report_language_source: str


class AiConfigurationSectionResponse(SchemaBase):
    ai_recommendations_enabled: bool
    waste_recommendations_auto_suggest: bool


class AnalysisConfigurationSectionResponse(SchemaBase):
    enabled_analysis_types: list[str]
    timeline_on_completion_enabled: bool
    default_analysis_title_template: str
    require_ai_insights_before_report: bool


class ReportPreferencesSectionResponse(SchemaBase):
    default_report_title_template: str
    auto_publish_on_generate: bool
    include_ai_sections_when_available: bool
    include_recommendations_section: bool
    include_scenario_provenance_section: bool


class PlatformDefaultNotificationPreferencesResponse(SchemaBase):
    notifications_enabled: bool
    enabled_notification_kinds: list[str]


class ResolvedSettingsResponse(SchemaBase):
    organization_id: UUID
    document_version: str
    organization_identity: OrganizationIdentityResponse
    organization_settings: OrganizationSettingsSectionResponse
    localization: LocalizationSectionResponse
    ai_configuration: AiConfigurationSectionResponse
    analysis_configuration: AnalysisConfigurationSectionResponse
    report_preferences: ReportPreferencesSectionResponse
    platform_default_notification_preferences: PlatformDefaultNotificationPreferencesResponse


def _reject_forbidden_keys(value: dict[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    for key in value:
        if key in FORBIDDEN_SETTINGS_KEYS:
            raise ValueError(
                f"Forbidden setting key '{key}' — deployment configuration "
                "cannot be overridden at organization level"
            )
    return value


class OrganizationSettingsSectionPatch(SchemaBase):
    locale: str | None = None
    date_display_format: str | None = None
    currency_display_code: str | None = None


class LocalizationSectionPatch(SchemaBase):
    prompt_language: str | None = None
    report_language: str | None = None


class AiConfigurationSectionPatch(SchemaBase):
    ai_recommendations_enabled: bool | None = None
    waste_recommendations_auto_suggest: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_forbidden(cls, data: Any) -> Any:
        if isinstance(data, dict):
            _reject_forbidden_keys(data)
        return data


class AnalysisConfigurationSectionPatch(SchemaBase):
    enabled_analysis_types: list[str] | None = None
    timeline_on_completion_enabled: bool | None = None
    default_analysis_title_template: str | None = None
    require_ai_insights_before_report: bool | None = None


class ReportPreferencesSectionPatch(SchemaBase):
    default_report_title_template: str | None = None
    auto_publish_on_generate: bool | None = None
    include_ai_sections_when_available: bool | None = None
    include_recommendations_section: bool | None = None
    include_scenario_provenance_section: bool | None = None


class PlatformDefaultNotificationPreferencesPatch(SchemaBase):
    notifications_enabled: bool | None = None
    enabled_notification_kinds: list[str] | None = None


class SettingsPatchRequest(SchemaBase):
    organization_settings: OrganizationSettingsSectionPatch | None = None
    localization: LocalizationSectionPatch | None = None
    ai_configuration: AiConfigurationSectionPatch | None = None
    analysis_configuration: AnalysisConfigurationSectionPatch | None = None
    report_preferences: ReportPreferencesSectionPatch | None = None
    platform_default_notification_preferences: (
        PlatformDefaultNotificationPreferencesPatch | None
    ) = Field(None, alias="platform_default_notification_preferences")

    model_config = {"populate_by_name": True}

    @field_validator("organization_settings", "localization", mode="before")
    @classmethod
    def validate_section_keys(cls, value: Any) -> Any:
        if isinstance(value, dict):
            _reject_forbidden_keys(value)
        return value

    def to_patch_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for field_name in (
            "organization_settings",
            "localization",
            "ai_configuration",
            "analysis_configuration",
            "report_preferences",
            "platform_default_notification_preferences",
        ):
            section = getattr(self, field_name)
            if section is not None:
                payload[field_name] = section.model_dump(exclude_unset=True)
        return payload
