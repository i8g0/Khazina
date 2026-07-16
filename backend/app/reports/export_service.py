"""Report binary export orchestration (Sprint 6.9)."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.reporting import Report
from app.db.models.report_export import ReportExport
from app.reports.constants import EXPORT_FORMAT_PDF
from app.reports.content import content_fingerprint
from app.reports.exceptions import ReportBuilderError
from app.reports.export_storage import ReportExportStorage
from app.reports.pdf_renderer import (
    export_fingerprint,
    preferences_fingerprint,
    render_pdf,
)
from app.repositories import AnalysisRepository, OrganizationRepository, ReportExportRepository, ReportRepository
from app.services.base import BaseService
from app.core.logging import get_logger
from app.observability.errors import classify_exception
from app.observability.persistence import merge_run_timeline
from app.observability.pipeline import PipelineStage, PipelineTimeline, load_pipeline_timeline
from app.observability.structured_log import log_pipeline_event
from app.services.exceptions import InvalidStateError, ResourceNotFoundError
from app.settings.service import SettingsService

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class PdfExportOutcome:
    export_record: ReportExport
    pdf_bytes: bytes
    created: bool


class ReportExportService(BaseService):
    """Deterministic PDF export from persisted Report Content Representation."""

    def __init__(
        self,
        session: Session,
        report_repository: ReportRepository,
        report_export_repository: ReportExportRepository,
        organization_repository: OrganizationRepository,
        export_storage: ReportExportStorage,
        *,
        analysis_repository: AnalysisRepository | None = None,
        settings_service: SettingsService | None = None,
    ) -> None:
        super().__init__(session)
        self._reports = report_repository
        self._exports = report_export_repository
        self._organizations = organization_repository
        self._analyses = analysis_repository
        self._storage = export_storage
        self._settings = settings_service

    def export_pdf(
        self,
        organization_id: uuid.UUID,
        report_id: uuid.UUID,
    ) -> PdfExportOutcome:
        self._require_organization(organization_id)
        report = self._owned_report(organization_id, report_id)
        if not report.content_representation:
            raise InvalidStateError(
                "Report has no generated content representation"
            )

        resolved = self._settings.get_resolved_settings(organization_id) if self._settings else None
        report_prefs = resolved.report_preferences if resolved else None
        if report_prefs is not None and not report_prefs.pdf_export_enabled:
            raise ReportBuilderError(
                code="pdf_export_disabled",
                message="PDF export is disabled for this organization",
            )

        content = dict(report.content_representation)
        content_fp = content_fingerprint(content)
        report_language = (
            resolved.localization.report_language if resolved else "ar"
        )
        include_cover = (
            report_prefs.pdf_include_cover_page if report_prefs else True
        )
        include_provenance = (
            report_prefs.pdf_include_provenance_appendix if report_prefs else False
        )
        prefs_fp = preferences_fingerprint(
            report_language=report_language,
            include_cover_page=include_cover,
            include_provenance_appendix=include_provenance,
        )

        existing = self._exports.get_by_dedup_key(
            report_id,
            EXPORT_FORMAT_PDF,
            content_fp,
            prefs_fp,
        )
        if existing is not None:
            self._record_pdf_timeline(
                organization_id,
                report,
                duration_ms=0,
                cached=True,
            )
            return PdfExportOutcome(
                export_record=existing,
                pdf_bytes=self._storage.read(existing.storage_reference),
                created=False,
            )

        export_started = time.perf_counter()
        timeline: PipelineTimeline | None = None
        if report.analysis_run_id and self._analyses is not None:
            run = self._analyses.get(report.analysis_run_id)
            if run is not None:
                timeline = PipelineTimeline(
                    organization_id=str(organization_id),
                    analysis_run_id=str(report.analysis_run_id),
                    inherited=load_pipeline_timeline(run.runtime_metadata),
                )
                timeline.start_stage(PipelineStage.PDF_EXPORT)
                log_pipeline_event(
                    logger,
                    "pipeline_stage",
                    stage=PipelineStage.PDF_EXPORT.value,
                    status="started",
                    organization_id=str(organization_id),
                    analysis_run_id=str(report.analysis_run_id),
                    report_id=str(report_id),
                )

        try:
            platform_name = (
                resolved.organization_identity.platform_name
                if resolved
                else "Khazina"
            )
            pdf_bytes = render_pdf(
                content,
                report_title=report.title,
                platform_name=platform_name,
                report_language=report_language,
                include_cover_page=include_cover,
                include_provenance_appendix=include_provenance,
            )
            export_fp = export_fingerprint(pdf_bytes)
            generated_at = datetime.now(timezone.utc)
            storage_reference = self._storage.save(
                organization_id,
                report_id,
                export_fp,
                pdf_bytes,
            )
            export_record = ReportExport(
                report_id=report_id,
                export_format=EXPORT_FORMAT_PDF,
                content_fingerprint=content_fp,
                preferences_fingerprint=prefs_fp,
                export_fingerprint=export_fp,
                file_size_bytes=len(pdf_bytes),
                storage_reference=storage_reference,
                generated_at=generated_at,
            )
            with self._transaction():
                self._exports.create(export_record)
        except Exception as exc:
            if timeline is not None and report.analysis_run_id and self._analyses is not None:
                run = self._analyses.get(report.analysis_run_id)
                if run is not None:
                    category = timeline.fail_stage(PipelineStage.PDF_EXPORT, exc)
                    self._analyses.update(
                        run,
                        {"runtime_metadata": merge_run_timeline(run, timeline)},
                    )
                    log_pipeline_event(
                        logger,
                        "pipeline_stage",
                        level=logging.WARNING,
                        stage=PipelineStage.PDF_EXPORT.value,
                        status="failed",
                        organization_id=str(organization_id),
                        analysis_run_id=str(report.analysis_run_id),
                        report_id=str(report_id),
                        error_category=category,
                        message=str(exc),
                    )
            raise

        self._record_pdf_timeline(
            organization_id,
            report,
            duration_ms=round((time.perf_counter() - export_started) * 1000, 2),
            cached=False,
            timeline=timeline,
        )
        return PdfExportOutcome(
            export_record=export_record,
            pdf_bytes=pdf_bytes,
            created=True,
        )

    def _record_pdf_timeline(
        self,
        organization_id: uuid.UUID,
        report: Report,
        *,
        duration_ms: float,
        cached: bool,
        timeline: PipelineTimeline | None = None,
    ) -> None:
        if not report.analysis_run_id or self._analyses is None:
            return
        run = self._analyses.get(report.analysis_run_id)
        if run is None:
            return
        if timeline is None:
            timeline = PipelineTimeline(
                organization_id=str(organization_id),
                analysis_run_id=str(report.analysis_run_id),
                inherited=load_pipeline_timeline(run.runtime_metadata),
            )
            timeline.start_stage(PipelineStage.PDF_EXPORT)
        timeline.complete_stage(PipelineStage.PDF_EXPORT, duration_ms=duration_ms)
        timeline.mark_completed()
        self._analyses.update(
            run,
            {"runtime_metadata": merge_run_timeline(run, timeline)},
        )
        log_pipeline_event(
            logger,
            "pipeline_stage",
            stage=PipelineStage.PDF_EXPORT.value,
            status="completed",
            organization_id=str(organization_id),
            analysis_run_id=str(report.analysis_run_id),
            report_id=str(report.id),
            duration_ms=duration_ms,
            message="cache_hit" if cached else "rendered",
        )

    def _owned_report(
        self, organization_id: uuid.UUID, report_id: uuid.UUID
    ):
        report = self._reports.get(report_id)
        if report is None:
            raise ResourceNotFoundError("Report", report_id)
        if report.organization_id != organization_id:
            raise ResourceNotFoundError("Report", report_id)
        return report

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
