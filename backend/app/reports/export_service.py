"""Report binary export orchestration (Sprint 6.9)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

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
from app.repositories import OrganizationRepository, ReportExportRepository, ReportRepository
from app.services.base import BaseService
from app.services.exceptions import InvalidStateError, ResourceNotFoundError
from app.settings.service import SettingsService


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
        settings_service: SettingsService | None = None,
    ) -> None:
        super().__init__(session)
        self._reports = report_repository
        self._exports = report_export_repository
        self._organizations = organization_repository
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
            report_prefs.pdf_include_provenance_appendix if report_prefs else True
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
            return PdfExportOutcome(
                export_record=existing,
                pdf_bytes=self._storage.read(existing.storage_reference),
                created=False,
            )

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
        return PdfExportOutcome(
            export_record=export_record,
            pdf_bytes=pdf_bytes,
            created=True,
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
