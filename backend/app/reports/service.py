"""Report Builder orchestration — persisted artifacts to Executive Report."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import Report
from app.db.models.enums import AnalysisRunStatus, AnalysisType, ReportStatus
from app.reports.constants import (
    ANALYSIS_TYPE_TO_PROFILE,
    ANALYSIS_TYPE_TO_REPORT_TYPE,
    PROFILE_RISK,
    PROFILE_SCENARIO,
    PROFILE_WASTE_DECISION,
    SUPPORTED_ANALYSIS_TYPES,
)
from app.reports.content import (
    ReportContentRepresentation,
    build_extended_metadata,
    canonical_serialize,
    content_fingerprint,
    default_document_version,
)
from app.reports.exceptions import ReportBuilderError
from app.reports.preferences import ReportAssemblyPreferences
from app.reports.loaders import (
    ReportInputLoader,
    risk_input_fingerprint,
    scenario_input_fingerprint,
    waste_input_fingerprint,
)
from app.reports.sections import (
    assemble_risk_sections,
    assemble_scenario_sections,
    assemble_waste_sections,
    derive_department_id,
)
from app.repositories import (
    AnalysisRepository,
    FinancialRepository,
    OrganizationRepository,
    RecommendationRepository,
    ReportRepository,
    RiskAnalysisRepository,
    RiskRepository,
    SimulationRepository,
    WasteRepository,
)
from app.services.base import BaseService
from app.core.logging import get_logger
from app.observability.errors import classify_exception
from app.observability.persistence import merge_run_timeline
from app.observability.pipeline import PipelineStage, PipelineTimeline, load_pipeline_timeline
from app.observability.structured_log import log_pipeline_event
from app.services.exceptions import InvalidStateError, ResourceNotFoundError
from app.settings.resolver import format_report_title
from app.settings.service import SettingsService
from app.notifications.builder import NotificationBuilder
from app.notifications.hooks import try_materialize

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ReportGenerationOutcome:
    report: Report
    content: ReportContentRepresentation
    export_serialization: str
    auto_publish_on_generate: bool = False


class ReportBuilderService(BaseService):
    """Deterministic executive report generation from persisted artifacts."""

    def __init__(
        self,
        session: Session,
        report_repository: ReportRepository,
        analysis_repository: AnalysisRepository,
        waste_repository: WasteRepository,
        simulation_repository: SimulationRepository,
        recommendation_repository: RecommendationRepository,
        organization_repository: OrganizationRepository,
        financial_repository: FinancialRepository,
        *,
        risk_analysis_repository: RiskAnalysisRepository | None = None,
        risk_repository: RiskRepository | None = None,
        input_loader: ReportInputLoader | None = None,
        settings_service: SettingsService | None = None,
        notification_builder: NotificationBuilder | None = None,
    ) -> None:
        super().__init__(session)
        self._reports = report_repository
        self._organizations = organization_repository
        self._analyses = analysis_repository
        self._settings = settings_service
        self._notifications = notification_builder
        self._input_loader = input_loader or ReportInputLoader(
            analysis_repository,
            waste_repository,
            simulation_repository,
            recommendation_repository,
            organization_repository,
            financial_repository,
            risk_analysis_repository,
            risk_repository,
        )

    def generate_report(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        title: str | None = None,
        department_id: uuid.UUID | None = None,
        generated_at: datetime | None = None,
        initiating_user_id: uuid.UUID | None = None,
    ) -> ReportGenerationOutcome:
        self._require_organization(organization_id)
        run = self._analyses.get(analysis_run_id)
        if run is None or run.organization_id != organization_id:
            raise ResourceNotFoundError("AnalysisRun", analysis_run_id)
        if run.status != AnalysisRunStatus.COMPLETED:
            raise InvalidStateError(
                f"Analysis run must be completed (current status: '{run.status}')"
            )
        if run.analysis_type not in SUPPORTED_ANALYSIS_TYPES:
            raise InvalidStateError(
                f"Analysis type '{run.analysis_type}' is not supported for report generation"
            )

        timeline = PipelineTimeline(
            organization_id=str(organization_id),
            file_id=str(run.source_file_id) if run.source_file_id else None,
            snapshot_id=str(run.source_snapshot_id) if run.source_snapshot_id else None,
            analysis_run_id=str(analysis_run_id),
            inherited=load_pipeline_timeline(run.runtime_metadata),
        )
        report_started = time.perf_counter()
        timeline.start_stage(PipelineStage.REPORT_GENERATION)
        log_pipeline_event(
            logger,
            "pipeline_stage",
            stage=PipelineStage.REPORT_GENERATION.value,
            status="started",
            organization_id=str(organization_id),
            analysis_run_id=str(analysis_run_id),
        )

        try:
            build_ts = generated_at or datetime.now(timezone.utc)
            profile = ANALYSIS_TYPE_TO_PROFILE[run.analysis_type]
            report_type = ANALYSIS_TYPE_TO_REPORT_TYPE[run.analysis_type]
            assembly_prefs = self._resolve_assembly_preferences(organization_id)

            if profile == PROFILE_WASTE_DECISION:
                inputs = self._input_loader.load_waste_inputs(
                    organization_id, analysis_run_id, run=run
                )
                if assembly_prefs.require_ai_insights_before_report:
                    insights = inputs.ai_insights or {}
                    if not insights.get("executive_summary"):
                        raise ReportBuilderError(
                            "ai_insights_required",
                            "Organization settings require AI insights before report generation",
                        )
                sections = assemble_waste_sections(
                    inputs,
                    include_ai_sections=assembly_prefs.include_ai_sections_when_available,
                    include_recommendations=assembly_prefs.include_recommendations_section,
                    report_language=assembly_prefs.report_language,
                    date_display_format=assembly_prefs.date_display_format,
                    currency_display_code=assembly_prefs.currency_display_code,
                )
                input_fp = waste_input_fingerprint(inputs)
                ai_consumed = bool(
                    inputs.ai_insights and inputs.ai_insights.get("executive_summary")
                )
                ai_generated_at = (
                    str(inputs.ai_insights.get("generated_at"))
                    if inputs.ai_insights and inputs.ai_insights.get("generated_at")
                    else None
                )
                baseline_run_id = None
                resolved_department = department_id or derive_department_id(
                    inputs.category_breakdowns
                )
                if title is None:
                    if self._settings is None:
                        default_title = f"{inputs.run.title} — تقرير تحليل"
                    else:
                        default_title = format_report_title(
                            assembly_prefs.default_report_title_template,
                            analysis_type=run.analysis_type,
                        )
                else:
                    default_title = f"{inputs.run.title} — تقرير تحليل"
                source_file_id = inputs.run.source_file_id
                reporting_period_id = inputs.run.reporting_period_id
            elif profile == PROFILE_SCENARIO:
                inputs = self._input_loader.load_scenario_inputs(
                    organization_id, analysis_run_id
                )
                sections = assemble_scenario_sections(
                    inputs,
                    include_scenario_provenance=(
                        assembly_prefs.include_scenario_provenance_section
                    ),
                    include_ai_sections=assembly_prefs.include_ai_sections_when_available,
                    report_language=assembly_prefs.report_language,
                    date_display_format=assembly_prefs.date_display_format,
                    currency_display_code=assembly_prefs.currency_display_code,
                )
                input_fp = scenario_input_fingerprint(inputs)
                ai_consumed = False
                ai_generated_at = None
                baseline_raw = inputs.scenario_provenance.get("baseline_analysis_run_id")
                baseline_run_id = str(baseline_raw) if baseline_raw else None
                resolved_department = department_id
                if title is None:
                    if self._settings is None:
                        default_title = f"{inputs.run.title} — تقرير محاكاة"
                    else:
                        default_title = format_report_title(
                            assembly_prefs.default_report_title_template,
                            analysis_type=run.analysis_type,
                        )
                else:
                    default_title = f"{inputs.run.title} — تقرير محاكاة"
                source_file_id = inputs.run.source_file_id
                reporting_period_id = inputs.run.reporting_period_id
            elif profile == PROFILE_RISK:
                inputs = self._input_loader.load_risk_inputs(
                    organization_id, analysis_run_id, run=run
                )
                sections = assemble_risk_sections(
                    inputs,
                    include_ai_sections=assembly_prefs.include_ai_sections_when_available,
                    include_recommendations=assembly_prefs.include_recommendations_section,
                    report_language=assembly_prefs.report_language,
                    date_display_format=assembly_prefs.date_display_format,
                    currency_display_code=assembly_prefs.currency_display_code,
                )
                input_fp = risk_input_fingerprint(inputs)
                ai_consumed = bool(
                    inputs.ai_insights
                    and inputs.ai_insights.get("risk_executive_summary")
                )
                ai_generated_at = (
                    str(inputs.ai_insights.get("generated_at"))
                    if inputs.ai_insights and inputs.ai_insights.get("generated_at")
                    else None
                )
                baseline_run_id = None
                resolved_department = department_id
                if title is None:
                    if self._settings is None:
                        default_title = f"{inputs.run.title} — تقرير مخاطر"
                    else:
                        default_title = format_report_title(
                            assembly_prefs.default_report_title_template,
                            analysis_type=run.analysis_type,
                        )
                else:
                    default_title = f"{inputs.run.title} — تقرير مخاطر"
                source_file_id = inputs.run.source_file_id
                reporting_period_id = inputs.run.reporting_period_id
            else:
                raise ReportBuilderError(
                    "unsupported_profile",
                    f"Unsupported report profile '{profile}'",
                )

            section_keys = tuple(section.key for section in sections)
            extended = build_extended_metadata(
                input_fingerprint=input_fp,
                sections_included=section_keys,
                ai_insights_consumed=ai_consumed,
                ai_insights_generated_at=ai_generated_at,
                baseline_run_id=baseline_run_id,
            )
            content = ReportContentRepresentation(
                report_document_version=default_document_version(),
                profile=profile,
                generated_at=build_ts,
                source_analysis_run_id=analysis_run_id,
                organization_id=organization_id,
                report_id=None,
                sections=sections,
                extended_metadata=extended,
            )
            summary = content.executive_summary_text()
            report_title = (title or default_title).strip()
            if not report_title:
                raise ReportBuilderError("invalid_title", "Report title must not be empty")

            with self._transaction():
                report = Report(
                    organization_id=organization_id,
                    department_id=resolved_department,
                    reporting_period_id=reporting_period_id,
                    source_file_id=source_file_id,
                    analysis_run_id=analysis_run_id,
                    title=report_title,
                    report_type=report_type,
                    status=ReportStatus.DRAFT.value,
                    summary=summary,
                    content_representation=None,
                )
                self._reports.create(report)
                final_content = content.with_report_id(report.id)
                payload = final_content.to_dict()
                payload["export_fingerprint"] = content_fingerprint(final_content)
                self._reports.update(
                    report,
                    {"content_representation": payload},
                )
                report.content_representation = payload

            timeline.complete_stage(PipelineStage.REPORT_GENERATION)
            self._analyses.update(
                run,
                {"runtime_metadata": merge_run_timeline(run, timeline)},
            )
            log_pipeline_event(
                logger,
                "pipeline_stage",
                stage=PipelineStage.REPORT_GENERATION.value,
                status="completed",
                organization_id=str(organization_id),
                analysis_run_id=str(analysis_run_id),
                report_id=str(report.id),
                duration_ms=round((time.perf_counter() - report_started) * 1000, 2),
            )
        except Exception as exc:
            category = classify_exception(exc)
            timeline.fail_stage(PipelineStage.REPORT_GENERATION, exc)
            self._analyses.update(
                run,
                {"runtime_metadata": merge_run_timeline(run, timeline)},
            )
            log_pipeline_event(
                logger,
                "pipeline_stage",
                level=logging.WARNING,
                stage=PipelineStage.REPORT_GENERATION.value,
                status="failed",
                organization_id=str(organization_id),
                analysis_run_id=str(analysis_run_id),
                error_category=category,
                message=str(exc),
            )
            raise

        try_materialize(
            self._notifications,
            initiating_user_id,
            lambda: self._notifications.materialize_report_generated(
                organization_id,
                report.id,
                initiating_user_id=initiating_user_id,
            ),
        )

        export_serialization = canonical_serialize(payload)
        return ReportGenerationOutcome(
            report=report,
            content=final_content,
            export_serialization=export_serialization,
            auto_publish_on_generate=assembly_prefs.auto_publish_on_generate,
        )

    def get_content_representation(
        self,
        organization_id: uuid.UUID,
        report_id: uuid.UUID,
    ) -> dict[str, Any]:
        report = self._owned_report(organization_id, report_id)
        if not report.content_representation:
            raise InvalidStateError(
                "Report has no generated content representation"
            )
        return dict(report.content_representation)

    def export_report(
        self,
        organization_id: uuid.UUID,
        report_id: uuid.UUID,
    ) -> str:
        payload = self.get_content_representation(organization_id, report_id)
        return canonical_serialize(payload)

    def _owned_report(
        self, organization_id: uuid.UUID, report_id: uuid.UUID
    ) -> Report:
        report = self._reports.get(report_id)
        if report is None:
            raise ResourceNotFoundError("Report", report_id)
        if report.organization_id != organization_id:
            raise ResourceNotFoundError("Report", report_id)
        return report

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)

    def _resolve_assembly_preferences(
        self, organization_id: uuid.UUID
    ) -> ReportAssemblyPreferences:
        if self._settings is None:
            return ReportAssemblyPreferences()
        resolved = self._settings.get_resolved_settings(organization_id)
        org_settings = resolved.organization_settings
        report_prefs = resolved.report_preferences
        return ReportAssemblyPreferences(
            include_ai_sections_when_available=(
                report_prefs.include_ai_sections_when_available
            ),
            include_recommendations_section=report_prefs.include_recommendations_section,
            include_scenario_provenance_section=(
                report_prefs.include_scenario_provenance_section
            ),
            report_language=resolved.localization.report_language,
            date_display_format=org_settings.date_display_format,
            currency_display_code=org_settings.currency_display_code,
            default_report_title_template=report_prefs.default_report_title_template,
            require_ai_insights_before_report=(
                resolved.analysis_configuration.require_ai_insights_before_report
            ),
            auto_publish_on_generate=report_prefs.auto_publish_on_generate,
        )
