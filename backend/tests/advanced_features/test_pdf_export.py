"""PDF export determinism tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.reports.content import build_extended_metadata, content_fingerprint
from app.reports.exceptions import ReportBuilderError
from app.reports.export_service import ReportExportService
from app.reports.pdf_renderer import export_fingerprint, preferences_fingerprint, render_pdf
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


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def report_id() -> uuid.UUID:
    return uuid.uuid4()


def _sample_content() -> dict:
    return {
        "report_document_version": "1.0",
        "profile": "waste_decision",
        "generated_at": "2026-07-15T12:00:00+00:00",
        "source_analysis_run_id": str(uuid.uuid4()),
        "organization_id": str(uuid.uuid4()),
        "report_id": str(uuid.uuid4()),
        "sections": [
            {"key": "cover", "payload": {"run_title": "Waste Q2"}},
            {"key": "executive_summary", "payload": {"text": "Summary"}},
        ],
        "extended_metadata": build_extended_metadata(
            input_fingerprint="abc",
            sections_included=("cover", "executive_summary"),
            ai_insights_consumed=False,
            ai_insights_generated_at=None,
            baseline_run_id=None,
        ).to_dict(),
    }


def test_pdf_render_is_deterministic() -> None:
    content = _sample_content()
    first = render_pdf(
        content,
        report_title="Report",
        platform_name="خزينة",
        report_language="ar",
        include_cover_page=True,
        include_provenance_appendix=True,
    )
    second = render_pdf(
        content,
        report_title="Report",
        platform_name="خزينة",
        report_language="ar",
        include_cover_page=True,
        include_provenance_appendix=True,
    )
    assert first == second
    assert export_fingerprint(first) == export_fingerprint(second)


def test_preferences_fingerprint_is_stable() -> None:
    first = preferences_fingerprint(
        report_language="ar",
        include_cover_page=True,
        include_provenance_appendix=False,
    )
    second = preferences_fingerprint(
        report_language="ar",
        include_cover_page=True,
        include_provenance_appendix=False,
    )
    assert first == second


def test_export_pdf_disabled_fails_closed(
    org_id: uuid.UUID, report_id: uuid.UUID
) -> None:
    session = MagicMock()
    report = MagicMock()
    report.id = report_id
    report.organization_id = org_id
    report.title = "Report"
    report.content_representation = _sample_content()

    report_repo = MagicMock()
    report_repo.get.return_value = report
    export_repo = MagicMock()
    export_repo.get_by_dedup_key.return_value = None
    org_repo = MagicMock()
    org_repo.get_organization.return_value = MagicMock()

    settings = MagicMock()
    settings.get_resolved_settings.return_value = ResolvedConfiguration(
        organization_id=str(org_id),
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
            pdf_export_enabled=False,
            pdf_include_cover_page=True,
            pdf_include_provenance_appendix=True,
        ),
        platform_default_notification_preferences=PlatformDefaultNotificationPreferencesSection(
            notifications_enabled=True,
            enabled_notification_kinds=frozenset(),
        ),
    )

    storage = MagicMock()
    service = ReportExportService(
        session,
        report_repo,
        export_repo,
        org_repo,
        storage,
        settings_service=settings,
    )

    with pytest.raises(ReportBuilderError):
        service.export_pdf(org_id, report_id)


def test_content_fingerprint_stable_for_export_idempotency() -> None:
    content = _sample_content()
    assert content_fingerprint(content) == content_fingerprint(dict(content))
