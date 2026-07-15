"""Consumer integration gate tests."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.ai_recommendations.pipeline import AiTaskPipeline
from app.ai_recommendations.service import AiRecommendationService
from app.db.models.enums import AnalysisRunStatus, AnalysisType
from app.services.analysis import AnalysisService
from app.settings.exceptions import AiRecommendationsDisabledError
from app.settings.models import (
    AiConfigurationSection,
    AnalysisConfigurationSection,
    LocalizationSection,
    OrganizationIdentityProjection,
    OrganizationSettingsSection,
    PlatformDefaultNotificationPreferencesSection,
    ReportPreferencesSection,
    ResolvedConfiguration,
)
from app.settings.service import SettingsService
from tests.ai_recommendations.conftest import MockOllamaByTask, sample_facts_contract


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


def _resolved_config(
    org_id: uuid.UUID,
    *,
    ai_enabled: bool = True,
    enabled_types: frozenset[str] | None = None,
    timeline_enabled: bool = True,
) -> ResolvedConfiguration:
    types = enabled_types or frozenset(
        {AnalysisType.FINANCIAL_WASTE.value, AnalysisType.SIMULATION.value}
    )
    return ResolvedConfiguration(
        organization_id=str(org_id),
        document_version="1.0",
        organization_identity=OrganizationIdentityProjection(
            name="Org",
            platform_name="خزينة",
            executive_title=None,
        ),
        organization_settings=OrganizationSettingsSection(
            locale="ar",
            date_display_format="gregorian",
            currency_display_code="SAR",
        ),
        localization=LocalizationSection(
            prompt_language="en",
            report_language="en",
            prompt_language_source="organization",
            report_language_source="organization",
        ),
        ai_configuration=AiConfigurationSection(
            ai_recommendations_enabled=ai_enabled,
            waste_recommendations_auto_suggest=True,
        ),
        analysis_configuration=AnalysisConfigurationSection(
            enabled_analysis_types=types,
            timeline_on_completion_enabled=timeline_enabled,
            default_analysis_title_template="{analysis_type}",
            require_ai_insights_before_report=False,
        ),
        report_preferences=ReportPreferencesSection(
            default_report_title_template="Executive Report — {analysis_type}",
            auto_publish_on_generate=False,
            include_ai_sections_when_available=True,
            include_recommendations_section=True,
            include_scenario_provenance_section=True,
            pdf_export_enabled=True,
            pdf_include_cover_page=True,
            pdf_include_provenance_appendix=True,
        ),
        platform_default_notification_preferences=PlatformDefaultNotificationPreferencesSection(
            notifications_enabled=True,
            enabled_notification_kinds=frozenset({"report_generated"}),
        ),
    )


def test_analysis_create_run_rejects_disabled_type(org_id: uuid.UUID) -> None:
    settings = MagicMock(spec=SettingsService)
    settings.get_resolved_settings.return_value = _resolved_config(
        org_id, enabled_types=frozenset({AnalysisType.SIMULATION.value})
    )
    service = AnalysisService(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        settings_service=settings,
    )
    service._require_organization = MagicMock()  # type: ignore[method-assign]
    with pytest.raises(Exception, match="disabled"):
        service.create_run(
            org_id,
            analysis_type=AnalysisType.FINANCIAL_WASTE.value,
            title="Run",
        )


def test_ai_recommendations_disabled_fails_closed(org_id: uuid.UUID) -> None:
    run_id = uuid.uuid4()
    facts = sample_facts_contract()
    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.analysis_type = AnalysisType.FINANCIAL_WASTE
    run.status = AnalysisRunStatus.COMPLETED
    run.runtime_metadata = {"facts_contract": facts.to_dict()}

    settings = MagicMock(spec=SettingsService)
    settings.get_resolved_settings.return_value = _resolved_config(
        org_id, ai_enabled=False
    )

    analysis_repo = MagicMock()
    analysis_repo.get.return_value = run
    waste_repo = MagicMock()
    waste_repo.get_result_for_run.return_value = MagicMock()

    service = AiRecommendationService(
        MagicMock(),
        analysis_repo,
        waste_repo,
        MagicMock(),
        task_pipeline=AiTaskPipeline(
            ollama_client=MockOllamaByTask(),
            ollama_model="test",
            prompt_language="ar",
        ),
        settings_service=settings,
    )
    with pytest.raises(AiRecommendationsDisabledError):
        service.generate_waste_recommendations(org_id, run_id)
