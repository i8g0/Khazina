"""Executive Reporting services: report drafting and publication workflow."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.db.models import Report, TimelineEvent
from app.db.models.enums import (
    RelatedEntityType,
    ReportStatus,
    ReportType,
    TimelineEventType,
)
from app.repositories import (
    AnalysisRepository,
    DepartmentRepository,
    FinancialRepository,
    OrganizationRepository,
    ReportRepository,
    TimelineRepository,
)
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    InvalidStateError,
    ResourceNotFoundError,
)
from app.notifications.builder import NotificationBuilder
from app.notifications.hooks import try_materialize


class ReportService(BaseService):
    """Business use cases for the published report catalog.

    Reports are drafted (``draft``) and then published (``ready``), which
    stamps ``published_at`` and appends a timeline event. Content generation
    is out of scope; this service manages the catalog workflow.
    """

    def __init__(
        self,
        session: Session,
        report_repository: ReportRepository,
        organization_repository: OrganizationRepository,
        department_repository: DepartmentRepository,
        analysis_repository: AnalysisRepository,
        financial_repository: FinancialRepository,
        timeline_repository: TimelineRepository,
        *,
        notification_builder: NotificationBuilder | None = None,
    ) -> None:
        super().__init__(session)
        self._reports = report_repository
        self._organizations = organization_repository
        self._departments = department_repository
        self._analyses = analysis_repository
        self._financials = financial_repository
        self._timeline = timeline_repository
        self._notifications = notification_builder

    # -- drafting -----------------------------------------------------------------

    def create_draft(
        self,
        organization_id: uuid.UUID,
        *,
        title: str,
        report_type: str,
        summary: str,
        department_id: uuid.UUID | None = None,
        reporting_period_id: uuid.UUID | None = None,
        source_file_id: uuid.UUID | None = None,
        analysis_run_id: uuid.UUID | None = None,
    ) -> Report:
        self._require_organization(organization_id)
        title = title.strip()
        summary = summary.strip()
        if not title or not summary:
            raise BusinessValidationError(
                "Report title and summary must not be empty"
            )
        if report_type not in set(ReportType):
            raise BusinessValidationError(f"Unknown report type '{report_type}'")

        if department_id is not None:
            department = self._departments.get(department_id)
            if department is None:
                raise ResourceNotFoundError("Department", department_id)
            self._check_ownership(department, "Department", organization_id)
        if reporting_period_id is not None:
            period = self._organizations.get_reporting_period(reporting_period_id)
            if period is None:
                raise ResourceNotFoundError("ReportingPeriod", reporting_period_id)
            self._check_ownership(period, "ReportingPeriod", organization_id)
        if source_file_id is not None:
            source_file = self._financials.get_file(source_file_id)
            if source_file is None:
                raise ResourceNotFoundError("FinancialFile", source_file_id)
            self._check_ownership(source_file, "FinancialFile", organization_id)
        if analysis_run_id is not None:
            run = self._analyses.get(analysis_run_id)
            if run is None:
                raise ResourceNotFoundError("AnalysisRun", analysis_run_id)
            self._check_ownership(run, "AnalysisRun", organization_id)

        report = Report(
            organization_id=organization_id,
            department_id=department_id,
            reporting_period_id=reporting_period_id,
            source_file_id=source_file_id,
            analysis_run_id=analysis_run_id,
            title=title,
            report_type=report_type,
            status=ReportStatus.DRAFT,
            summary=summary,
        )
        with self._transaction():
            self._reports.create(report)
        return report

    # -- retrieval -----------------------------------------------------------------

    def get_report(self, report_id: uuid.UUID) -> Report:
        return self._found(self._reports.get(report_id), "Report", report_id)

    def list_reports(
        self,
        organization_id: uuid.UUID,
        *,
        report_type: str | None = None,
        status: str | None = None,
        department_id: uuid.UUID | None = None,
        reporting_period_id: uuid.UUID | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Report]:
        self._require_organization(organization_id)
        return self._reports.list_for_organization(
            organization_id,
            report_type=report_type,
            status=status,
            department_id=department_id,
            reporting_period_id=reporting_period_id,
            limit=limit,
            offset=offset,
        )

    # -- workflow ---------------------------------------------------------------------

    def update_draft(
        self,
        organization_id: uuid.UUID,
        report_id: uuid.UUID,
        *,
        title: str | None = None,
        summary: str | None = None,
    ) -> Report:
        report = self._owned_report(organization_id, report_id)
        if report.status != ReportStatus.DRAFT:
            raise InvalidStateError("Only draft reports can be edited")

        values: dict[str, object] = {}
        if title is not None:
            title = title.strip()
            if not title:
                raise BusinessValidationError("Report title must not be empty")
            values["title"] = title
        if summary is not None:
            summary = summary.strip()
            if not summary:
                raise BusinessValidationError("Report summary must not be empty")
            values["summary"] = summary
        if not values:
            return report

        with self._transaction():
            self._reports.update(report, values)
        return report

    def publish_report(
        self,
        organization_id: uuid.UUID,
        report_id: uuid.UUID,
        *,
        initiating_user_id: uuid.UUID | None = None,
    ) -> Report:
        """Publishes a draft: sets ready status, stamps the date, logs the event."""
        report = self._owned_report(organization_id, report_id)
        if report.status != ReportStatus.DRAFT:
            raise InvalidStateError("Only draft reports can be published")
        published_at = date.today()

        with self._transaction():
            self._reports.update(
                report,
                {"status": ReportStatus.READY, "published_at": published_at},
            )
            self._timeline.create(
                TimelineEvent(
                    organization_id=organization_id,
                    reporting_period_id=report.reporting_period_id,
                    event_date=published_at,
                    title=report.title,
                    event_type=TimelineEventType.REPORT,
                    related_entity_type=RelatedEntityType.REPORT,
                    related_entity_id=report.id,
                )
            )
        try_materialize(
            self._notifications,
            initiating_user_id,
            lambda: self._notifications.materialize_report_published(
                organization_id,
                report_id,
                initiating_user_id=initiating_user_id,
            ),
        )
        return report

    def delete_report(self, organization_id: uuid.UUID, report_id: uuid.UUID) -> None:
        report = self._owned_report(organization_id, report_id)
        with self._transaction():
            self._reports.delete(report)

    # -- internals ---------------------------------------------------------------------

    def _owned_report(
        self, organization_id: uuid.UUID, report_id: uuid.UUID
    ) -> Report:
        report = self.get_report(report_id)
        self._check_ownership(report, "Report", organization_id)
        return report

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
