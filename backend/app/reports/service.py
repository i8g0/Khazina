"""Report Builder orchestration — persisted artifacts to Executive Report."""

from __future__ import annotations

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
from app.reports.loaders import (
    ReportInputLoader,
    scenario_input_fingerprint,
    waste_input_fingerprint,
)
from app.reports.sections import (
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
    SimulationRepository,
    WasteRepository,
)
from app.services.base import BaseService
from app.services.exceptions import InvalidStateError, ResourceNotFoundError


@dataclass(frozen=True, slots=True)
class ReportGenerationOutcome:
    report: Report
    content: ReportContentRepresentation
    export_serialization: str


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
        input_loader: ReportInputLoader | None = None,
    ) -> None:
        super().__init__(session)
        self._reports = report_repository
        self._organizations = organization_repository
        self._analyses = analysis_repository
        self._input_loader = input_loader or ReportInputLoader(
            analysis_repository,
            waste_repository,
            simulation_repository,
            recommendation_repository,
            organization_repository,
            financial_repository,
        )

    def generate_report(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        title: str | None = None,
        department_id: uuid.UUID | None = None,
        generated_at: datetime | None = None,
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

        build_ts = generated_at or datetime.now(timezone.utc)
        profile = ANALYSIS_TYPE_TO_PROFILE[run.analysis_type]
        report_type = ANALYSIS_TYPE_TO_REPORT_TYPE[run.analysis_type]

        if profile == PROFILE_WASTE_DECISION:
            inputs = self._input_loader.load_waste_inputs(organization_id, analysis_run_id)
            sections = assemble_waste_sections(inputs)
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
            default_title = f"{inputs.run.title} — تقرير تحليل"
            source_file_id = inputs.run.source_file_id
            reporting_period_id = inputs.run.reporting_period_id
        elif profile == PROFILE_SCENARIO:
            inputs = self._input_loader.load_scenario_inputs(
                organization_id, analysis_run_id
            )
            sections = assemble_scenario_sections(inputs)
            input_fp = scenario_input_fingerprint(inputs)
            ai_consumed = False
            ai_generated_at = None
            baseline_raw = inputs.scenario_provenance.get("baseline_analysis_run_id")
            baseline_run_id = str(baseline_raw) if baseline_raw else None
            resolved_department = department_id
            default_title = f"{inputs.run.title} — تقرير محاكاة"
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

        export_serialization = canonical_serialize(payload)
        return ReportGenerationOutcome(
            report=report,
            content=final_content,
            export_serialization=export_serialization,
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
