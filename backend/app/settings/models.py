"""Resolved and persisted settings document shapes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class OrganizationIdentityProjection:
    name: str
    platform_name: str
    executive_title: str | None


@dataclass(frozen=True, slots=True)
class OrganizationSettingsSection:
    locale: str
    date_display_format: str
    currency_display_code: str


@dataclass(frozen=True, slots=True)
class LocalizationSection:
    prompt_language: str
    report_language: str
    prompt_language_source: str
    report_language_source: str


@dataclass(frozen=True, slots=True)
class AiConfigurationSection:
    ai_recommendations_enabled: bool
    waste_recommendations_auto_suggest: bool


@dataclass(frozen=True, slots=True)
class AnalysisConfigurationSection:
    enabled_analysis_types: frozenset[str]
    timeline_on_completion_enabled: bool
    default_analysis_title_template: str
    require_ai_insights_before_report: bool


@dataclass(frozen=True, slots=True)
class ReportPreferencesSection:
    default_report_title_template: str
    auto_publish_on_generate: bool
    include_ai_sections_when_available: bool
    include_recommendations_section: bool
    include_scenario_provenance_section: bool
    pdf_export_enabled: bool
    pdf_include_cover_page: bool
    pdf_include_provenance_appendix: bool


@dataclass(frozen=True, slots=True)
class PlatformDefaultNotificationPreferencesSection:
    notifications_enabled: bool
    enabled_notification_kinds: frozenset[str]


@dataclass(frozen=True, slots=True)
class ResolvedConfiguration:
    organization_id: str
    document_version: str
    organization_identity: OrganizationIdentityProjection
    organization_settings: OrganizationSettingsSection
    localization: LocalizationSection
    ai_configuration: AiConfigurationSection
    analysis_configuration: AnalysisConfigurationSection
    report_preferences: ReportPreferencesSection
    platform_default_notification_preferences: PlatformDefaultNotificationPreferencesSection

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "organization_id": self.organization_id,
            "document_version": self.document_version,
            "organization_identity": {
                "name": self.organization_identity.name,
                "platform_name": self.organization_identity.platform_name,
                "executive_title": self.organization_identity.executive_title,
            },
            "organization_settings": {
                "locale": self.organization_settings.locale,
                "date_display_format": self.organization_settings.date_display_format,
                "currency_display_code": self.organization_settings.currency_display_code,
            },
            "localization": {
                "prompt_language": self.localization.prompt_language,
                "report_language": self.localization.report_language,
                "prompt_language_source": self.localization.prompt_language_source,
                "report_language_source": self.localization.report_language_source,
            },
            "ai_configuration": {
                "ai_recommendations_enabled": (
                    self.ai_configuration.ai_recommendations_enabled
                ),
                "waste_recommendations_auto_suggest": (
                    self.ai_configuration.waste_recommendations_auto_suggest
                ),
            },
            "analysis_configuration": {
                "enabled_analysis_types": sorted(
                    self.analysis_configuration.enabled_analysis_types
                ),
                "timeline_on_completion_enabled": (
                    self.analysis_configuration.timeline_on_completion_enabled
                ),
                "default_analysis_title_template": (
                    self.analysis_configuration.default_analysis_title_template
                ),
                "require_ai_insights_before_report": (
                    self.analysis_configuration.require_ai_insights_before_report
                ),
            },
            "report_preferences": {
                "default_report_title_template": (
                    self.report_preferences.default_report_title_template
                ),
                "auto_publish_on_generate": (
                    self.report_preferences.auto_publish_on_generate
                ),
                "include_ai_sections_when_available": (
                    self.report_preferences.include_ai_sections_when_available
                ),
                "include_recommendations_section": (
                    self.report_preferences.include_recommendations_section
                ),
                "include_scenario_provenance_section": (
                    self.report_preferences.include_scenario_provenance_section
                ),
                "pdf_export_enabled": self.report_preferences.pdf_export_enabled,
                "pdf_include_cover_page": (
                    self.report_preferences.pdf_include_cover_page
                ),
                "pdf_include_provenance_appendix": (
                    self.report_preferences.pdf_include_provenance_appendix
                ),
            },
            "platform_default_notification_preferences": {
                "notifications_enabled": (
                    self.platform_default_notification_preferences.notifications_enabled
                ),
                "enabled_notification_kinds": sorted(
                    self.platform_default_notification_preferences.enabled_notification_kinds
                ),
            },
        }


@dataclass(slots=True)
class PersistedSettingsDocument:
    """Partial overrides stored per organization."""

    organization_settings: dict[str, Any] = field(default_factory=dict)
    localization: dict[str, Any] = field(default_factory=dict)
    ai_configuration: dict[str, Any] = field(default_factory=dict)
    analysis_configuration: dict[str, Any] = field(default_factory=dict)
    report_preferences: dict[str, Any] = field(default_factory=dict)
    platform_default_notification_preferences: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PersistedSettingsDocument:
        if not data:
            return cls()
        return cls(
            organization_settings=dict(data.get("organization_settings") or {}),
            localization=dict(data.get("localization") or {}),
            ai_configuration=dict(data.get("ai_configuration") or {}),
            analysis_configuration=dict(data.get("analysis_configuration") or {}),
            report_preferences=dict(data.get("report_preferences") or {}),
            platform_default_notification_preferences=dict(
                data.get("platform_default_notification_preferences") or {}
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.organization_settings:
            payload["organization_settings"] = self.organization_settings
        if self.localization:
            payload["localization"] = self.localization
        if self.ai_configuration:
            payload["ai_configuration"] = self.ai_configuration
        if self.analysis_configuration:
            payload["analysis_configuration"] = self.analysis_configuration
        if self.report_preferences:
            payload["report_preferences"] = self.report_preferences
        if self.platform_default_notification_preferences:
            payload["platform_default_notification_preferences"] = (
                self.platform_default_notification_preferences
            )
        return payload
