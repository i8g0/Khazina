"""Deterministic settings resolution and validation."""

from __future__ import annotations

from typing import Any

from app.core.config import settings as deployment_settings
from app.db.models import Organization
from app.db.models.enums import AnalysisType
from app.settings.constants import (
    DEFAULT_ANALYSIS_TITLE_TEMPLATE,
    DEFAULT_CURRENCY_DISPLAY_CODE,
    DEFAULT_DATE_DISPLAY_FORMAT,
    DEFAULT_ENABLED_ANALYSIS_TYPES,
    DEFAULT_ENABLED_NOTIFICATION_KINDS,
    DEFAULT_LOCALE,
    DEFAULT_REPORT_TITLE_TEMPLATE,
    DOCUMENT_VERSION,
    FORBIDDEN_SETTINGS_KEYS,
    VALID_DATE_DISPLAY_FORMATS,
)
from app.settings.exceptions import SettingsValidationError
from app.settings.models import (
    AiConfigurationSection,
    AnalysisConfigurationSection,
    LocalizationSection,
    OrganizationIdentityProjection,
    OrganizationSettingsSection,
    PersistedSettingsDocument,
    PlatformDefaultNotificationPreferencesSection,
    ReportPreferencesSection,
    ResolvedConfiguration,
)


def _deployment_prompt_language() -> str:
    return deployment_settings.ai.default_prompt_language


def platform_default_document() -> PersistedSettingsDocument:
    """Authoritative platform defaults — not persisted until lazy init."""
    return PersistedSettingsDocument()


def _coalesce_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise SettingsValidationError(f"Expected boolean, got {type(value).__name__}")
    return value


def _coalesce_str(value: Any, default: str) -> str:
    if value is None:
        return default
    if not isinstance(value, str) or not value.strip():
        raise SettingsValidationError("String setting must not be empty")
    return value.strip()


def _coalesce_analysis_types(value: Any) -> frozenset[str]:
    if value is None:
        return DEFAULT_ENABLED_ANALYSIS_TYPES
    if not isinstance(value, list) or not value:
        raise SettingsValidationError("enabled_analysis_types must be a non-empty list")
    normalized = frozenset(str(item) for item in value)
    unknown = normalized - set(AnalysisType)
    if unknown:
        raise SettingsValidationError(
            f"Unknown analysis types: {', '.join(sorted(unknown))}"
        )
    return normalized


def _coalesce_notification_kinds(value: Any) -> frozenset[str]:
    if value is None:
        return DEFAULT_ENABLED_NOTIFICATION_KINDS
    if not isinstance(value, list):
        raise SettingsValidationError("enabled_notification_kinds must be a list")
    normalized = frozenset(str(item) for item in value)
    unknown = normalized - DEFAULT_ENABLED_NOTIFICATION_KINDS
    if unknown:
        raise SettingsValidationError(
            f"Unknown notification kinds: {', '.join(sorted(unknown))}"
        )
    return normalized


def _resolve_localization(
    overrides: dict[str, Any],
) -> LocalizationSection:
    deployment_lang = _deployment_prompt_language()
    prompt_override = overrides.get("prompt_language")
    report_override = overrides.get("report_language")

    if prompt_override is not None:
        if not isinstance(prompt_override, str) or not prompt_override.strip():
            raise SettingsValidationError("prompt_language must be a non-empty string")
        prompt_language = prompt_override.strip().lower()
        prompt_source = "organization"
    else:
        prompt_language = deployment_lang
        prompt_source = "deployment"

    if report_override is not None:
        if not isinstance(report_override, str) or not report_override.strip():
            raise SettingsValidationError("report_language must be a non-empty string")
        report_language = report_override.strip().lower()
        report_source = "organization"
    elif prompt_override is not None:
        report_language = prompt_language
        report_source = "prompt_language"
    else:
        report_language = deployment_lang
        report_source = "deployment"

    return LocalizationSection(
        prompt_language=prompt_language,
        report_language=report_language,
        prompt_language_source=prompt_source,
        report_language_source=report_source,
    )


def resolve_configuration(
    organization: Organization,
    persisted: PersistedSettingsDocument,
) -> ResolvedConfiguration:
    org_overrides = persisted.organization_settings
    loc_overrides = persisted.localization
    ai_overrides = persisted.ai_configuration
    analysis_overrides = persisted.analysis_configuration
    report_overrides = persisted.report_preferences
    notification_overrides = persisted.platform_default_notification_preferences

    locale = _coalesce_str(org_overrides.get("locale"), DEFAULT_LOCALE)
    date_format = org_overrides.get("date_display_format", DEFAULT_DATE_DISPLAY_FORMAT)
    if date_format not in VALID_DATE_DISPLAY_FORMATS:
        raise SettingsValidationError(
            f"date_display_format must be one of {sorted(VALID_DATE_DISPLAY_FORMATS)}"
        )

    organization_settings = OrganizationSettingsSection(
        locale=locale.lower(),
        date_display_format=str(date_format),
        currency_display_code=_coalesce_str(
            org_overrides.get("currency_display_code"),
            DEFAULT_CURRENCY_DISPLAY_CODE,
        ).upper(),
    )

    localization = _resolve_localization(loc_overrides)

    ai_configuration = AiConfigurationSection(
        ai_recommendations_enabled=_coalesce_bool(
            ai_overrides.get("ai_recommendations_enabled"), True
        ),
        waste_recommendations_auto_suggest=_coalesce_bool(
            ai_overrides.get("waste_recommendations_auto_suggest"), True
        ),
    )

    analysis_configuration = AnalysisConfigurationSection(
        enabled_analysis_types=_coalesce_analysis_types(
            analysis_overrides.get("enabled_analysis_types")
        ),
        timeline_on_completion_enabled=_coalesce_bool(
            analysis_overrides.get("timeline_on_completion_enabled"), True
        ),
        default_analysis_title_template=_coalesce_str(
            analysis_overrides.get("default_analysis_title_template"),
            DEFAULT_ANALYSIS_TITLE_TEMPLATE,
        ),
        require_ai_insights_before_report=_coalesce_bool(
            analysis_overrides.get("require_ai_insights_before_report"), False
        ),
    )

    report_preferences = ReportPreferencesSection(
        default_report_title_template=_coalesce_str(
            report_overrides.get("default_report_title_template"),
            DEFAULT_REPORT_TITLE_TEMPLATE,
        ),
        auto_publish_on_generate=_coalesce_bool(
            report_overrides.get("auto_publish_on_generate"), False
        ),
        include_ai_sections_when_available=_coalesce_bool(
            report_overrides.get("include_ai_sections_when_available"), True
        ),
        include_recommendations_section=_coalesce_bool(
            report_overrides.get("include_recommendations_section"), True
        ),
        include_scenario_provenance_section=_coalesce_bool(
            report_overrides.get("include_scenario_provenance_section"), True
        ),
    )

    platform_default_notification_preferences = PlatformDefaultNotificationPreferencesSection(
        notifications_enabled=_coalesce_bool(
            notification_overrides.get("notifications_enabled"), True
        ),
        enabled_notification_kinds=_coalesce_notification_kinds(
            notification_overrides.get("enabled_notification_kinds")
        ),
    )

    return ResolvedConfiguration(
        organization_id=str(organization.id),
        document_version=DOCUMENT_VERSION,
        organization_identity=OrganizationIdentityProjection(
            name=organization.name,
            platform_name=organization.platform_name,
            executive_title=organization.executive_title,
        ),
        organization_settings=organization_settings,
        localization=localization,
        ai_configuration=ai_configuration,
        analysis_configuration=analysis_configuration,
        report_preferences=report_preferences,
        platform_default_notification_preferences=platform_default_notification_preferences,
    )


def merge_patch(
    persisted: PersistedSettingsDocument,
    patch: dict[str, Any],
) -> PersistedSettingsDocument:
    """Deep-merge a validated PATCH payload into persisted overrides."""
    merged = PersistedSettingsDocument.from_dict(persisted.to_dict())

    for section_name, section_patch in patch.items():
        if section_patch is None:
            continue
        if not isinstance(section_patch, dict):
            raise SettingsValidationError(
                f"Section '{section_name}' must be an object"
            )
        _reject_forbidden_keys(section_patch)
        target = getattr(merged, section_name)
        for key, value in section_patch.items():
            if value is None:
                target.pop(key, None)
            else:
                target[key] = value

    return merged


def _reject_forbidden_keys(payload: dict[str, Any], *, path: str = "") -> None:
    for key, value in payload.items():
        current = f"{path}.{key}" if path else key
        if key in FORBIDDEN_SETTINGS_KEYS:
            raise SettingsValidationError(
                f"Forbidden setting key '{current}' — deployment configuration "
                "cannot be overridden at organization level"
            )
        if isinstance(value, dict):
            _reject_forbidden_keys(value, path=current)


def validate_patch_payload(patch: dict[str, Any]) -> None:
    _reject_forbidden_keys(patch)
    allowed_sections = {
        "organization_settings",
        "localization",
        "ai_configuration",
        "analysis_configuration",
        "report_preferences",
        "platform_default_notification_preferences",
    }
    unknown = set(patch) - allowed_sections
    if unknown:
        raise SettingsValidationError(
            f"Unknown settings sections: {', '.join(sorted(unknown))}"
        )


def format_analysis_title(
    template: str,
    *,
    analysis_type: str,
    reporting_period_label: str = "",
) -> str:
    return template.format(
        analysis_type=analysis_type,
        reporting_period_label=reporting_period_label or "—",
    )


def format_report_title(template: str, *, analysis_type: str) -> str:
    return template.format(analysis_type=analysis_type)
