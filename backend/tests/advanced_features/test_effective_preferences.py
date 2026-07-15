"""Effective notification preference merge tests."""

from __future__ import annotations

import uuid

from app.db.models import Organization
from app.notifications.constants import (
    KIND_ANALYSIS_COMPLETED,
    KIND_REPORT_GENERATED,
)
from app.notifications.effective_preferences import (
    is_effective_notification_materialization_enabled,
)
from app.notifications.models import ResolvedUserNotificationPreferences
from app.settings.models import (
    OrganizationIdentityProjection,
    OrganizationSettingsSection,
    AiConfigurationSection,
    AnalysisConfigurationSection,
    LocalizationSection,
    PlatformDefaultNotificationPreferencesSection,
    ReportPreferencesSection,
    ResolvedConfiguration,
)
from app.settings.constants import DEFAULT_ENABLED_NOTIFICATION_KINDS


def _resolved(*, org_enabled: bool = True, org_kinds: frozenset[str] | None = None):
    org = Organization(name="Org", platform_name="خزينة")
    org.id = uuid.uuid4()
    return ResolvedConfiguration(
        organization_id=str(org.id),
        document_version="1.0",
        organization_identity=OrganizationIdentityProjection(
            name="Org", platform_name="خزينة", executive_title=None
        ),
        organization_settings=OrganizationSettingsSection(
            locale="ar", date_display_format="gregorian", currency_display_code="SAR"
        ),
        localization=LocalizationSection(
            prompt_language="ar",
            report_language="ar",
            prompt_language_source="deployment",
            report_language_source="deployment",
        ),
        ai_configuration=AiConfigurationSection(
            ai_recommendations_enabled=True,
            waste_recommendations_auto_suggest=True,
        ),
        analysis_configuration=AnalysisConfigurationSection(
            enabled_analysis_types=frozenset({"financial_waste"}),
            timeline_on_completion_enabled=True,
            default_analysis_title_template="t",
            require_ai_insights_before_report=False,
        ),
        report_preferences=ReportPreferencesSection(
            default_report_title_template="r",
            auto_publish_on_generate=False,
            include_ai_sections_when_available=True,
            include_recommendations_section=True,
            include_scenario_provenance_section=True,
            pdf_export_enabled=True,
            pdf_include_cover_page=True,
            pdf_include_provenance_appendix=True,
        ),
        platform_default_notification_preferences=PlatformDefaultNotificationPreferencesSection(
            notifications_enabled=org_enabled,
            enabled_notification_kinds=org_kinds or DEFAULT_ENABLED_NOTIFICATION_KINDS,
        ),
    )


def test_org_master_switch_blocks_all() -> None:
    resolved = _resolved(org_enabled=False)
    user = ResolvedUserNotificationPreferences(
        notifications_enabled=True,
        muted_notification_kinds=frozenset(),
        preferences_version="1.0",
    )
    assert not is_effective_notification_materialization_enabled(
        resolved, user, KIND_ANALYSIS_COMPLETED
    )


def test_user_master_switch_blocks() -> None:
    resolved = _resolved()
    user = ResolvedUserNotificationPreferences(
        notifications_enabled=False,
        muted_notification_kinds=frozenset(),
        preferences_version="1.0",
    )
    assert not is_effective_notification_materialization_enabled(
        resolved, user, KIND_ANALYSIS_COMPLETED
    )


def test_user_mute_suppresses_kind() -> None:
    resolved = _resolved()
    user = ResolvedUserNotificationPreferences(
        notifications_enabled=True,
        muted_notification_kinds=frozenset({KIND_REPORT_GENERATED}),
        preferences_version="1.0",
    )
    assert is_effective_notification_materialization_enabled(
        resolved, user, KIND_ANALYSIS_COMPLETED
    )
    assert not is_effective_notification_materialization_enabled(
        resolved, user, KIND_REPORT_GENERATED
    )


def test_org_disabled_kind_not_enabled_for_user() -> None:
    resolved = _resolved(org_kinds=frozenset({KIND_ANALYSIS_COMPLETED}))
    assert not is_effective_notification_materialization_enabled(
        resolved, None, KIND_REPORT_GENERATED
    )
