"""Shared Analysis services: analysis run lifecycle orchestration."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AnalysisRun, TimelineEvent
from app.db.models.enums import (
    AnalysisRunStatus,
    AnalysisType,
    ProcessingStatus,
    RelatedEntityType,
    TimelineEventType,
)
from app.repositories import (
    AnalysisRepository,
    FinancialRepository,
    OrganizationRepository,
    TimelineRepository,
)
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    InvalidStateError,
    InvalidStateTransitionError,
    ResourceNotFoundError,
)

# Approved run lifecycle (design §4.5): pending → processing → completed/failed.
_RUN_TRANSITIONS: dict[str, set[str]] = {
    AnalysisRunStatus.PENDING: {AnalysisRunStatus.PROCESSING},
    AnalysisRunStatus.PROCESSING: {
        AnalysisRunStatus.COMPLETED,
        AnalysisRunStatus.FAILED,
    },
    AnalysisRunStatus.COMPLETED: set(),
    AnalysisRunStatus.FAILED: set(),
}


class AnalysisService(BaseService):
    """Business use cases for the shared analysis-run parent entity.

    Orchestrates run creation and lifecycle transitions. AI execution itself
    is out of scope; this service prepares and finalizes the workflow that a
    future execution engine will drive.
    """

    def __init__(
        self,
        session: Session,
        analysis_repository: AnalysisRepository,
        organization_repository: OrganizationRepository,
        financial_repository: FinancialRepository,
        timeline_repository: TimelineRepository,
    ) -> None:
        super().__init__(session)
        self._analyses = analysis_repository
        self._organizations = organization_repository
        self._financials = financial_repository
        self._timeline = timeline_repository

    # -- run creation -----------------------------------------------------------

    def create_run(
        self,
        organization_id: uuid.UUID,
        *,
        analysis_type: str,
        title: str,
        source_file_id: uuid.UUID | None = None,
        reporting_period_id: uuid.UUID | None = None,
        runtime_metadata: dict[str, Any] | None = None,
    ) -> AnalysisRun:
        """Creates a pending run; file-based analyses require an analyzable file."""
        self._require_organization(organization_id)
        title = title.strip()
        if not title:
            raise BusinessValidationError("Analysis title must not be empty")
        if analysis_type not in set(AnalysisType):
            raise BusinessValidationError(f"Unknown analysis type '{analysis_type}'")

        if source_file_id is not None:
            source_file = self._financials.get_file(source_file_id)
            if source_file is None:
                raise ResourceNotFoundError("FinancialFile", source_file_id)
            self._check_ownership(source_file, "FinancialFile", organization_id)
            if source_file.processing_status != ProcessingStatus.READY_FOR_ANALYSIS:
                raise InvalidStateError(
                    "Source file must be ready for analysis before a run can "
                    f"start (current status: '{source_file.processing_status}')"
                )

        if reporting_period_id is not None:
            period = self._organizations.get_reporting_period(reporting_period_id)
            if period is None:
                raise ResourceNotFoundError("ReportingPeriod", reporting_period_id)
            self._check_ownership(period, "ReportingPeriod", organization_id)

        run = AnalysisRun(
            organization_id=organization_id,
            reporting_period_id=reporting_period_id,
            source_file_id=source_file_id,
            analysis_type=analysis_type,
            title=title,
            status=AnalysisRunStatus.PENDING,
            runtime_metadata=runtime_metadata,
        )
        with self._transaction():
            self._analyses.create(run)
        return run

    # -- lookups -----------------------------------------------------------------

    def get_run(self, run_id: uuid.UUID) -> AnalysisRun:
        return self._found(self._analyses.get(run_id), "AnalysisRun", run_id)

    def list_runs(
        self,
        organization_id: uuid.UUID,
        *,
        analysis_type: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AnalysisRun]:
        self._require_organization(organization_id)
        return self._analyses.list_for_organization(
            organization_id,
            analysis_type=analysis_type,
            status=status,
            limit=limit,
            offset=offset,
        )

    def list_recent_completed(
        self, organization_id: uuid.UUID, *, limit: int = 10
    ) -> list[AnalysisRun]:
        self._require_organization(organization_id)
        return self._analyses.list_recent_completed(organization_id, limit=limit)

    # -- lifecycle ------------------------------------------------------------------

    def start_run(self, organization_id: uuid.UUID, run_id: uuid.UUID) -> AnalysisRun:
        run = self._owned_run(organization_id, run_id)
        self._validate_transition(run, AnalysisRunStatus.PROCESSING)
        with self._transaction():
            self._analyses.update(
                run,
                {
                    "status": AnalysisRunStatus.PROCESSING,
                    "started_at": datetime.now(timezone.utc),
                },
            )
        return run

    def complete_run(
        self, organization_id: uuid.UUID, run_id: uuid.UUID
    ) -> AnalysisRun:
        """Finalizes a run and appends the corresponding timeline event."""
        run = self._owned_run(organization_id, run_id)
        self._validate_transition(run, AnalysisRunStatus.COMPLETED)
        completed_at = datetime.now(timezone.utc)

        with self._transaction():
            self._analyses.update(
                run,
                {
                    "status": AnalysisRunStatus.COMPLETED,
                    "completed_at": completed_at,
                },
            )
            self._timeline.create(
                TimelineEvent(
                    organization_id=organization_id,
                    reporting_period_id=run.reporting_period_id,
                    event_date=completed_at.date(),
                    title=run.title,
                    event_type=TimelineEventType.ANALYSIS,
                    related_entity_type=RelatedEntityType.ANALYSIS_RUN,
                    related_entity_id=run.id,
                )
            )
        return run

    def fail_run(
        self,
        organization_id: uuid.UUID,
        run_id: uuid.UUID,
        *,
        failure_details: dict[str, Any] | None = None,
    ) -> AnalysisRun:
        run = self._owned_run(organization_id, run_id)
        self._validate_transition(run, AnalysisRunStatus.FAILED)

        values: dict[str, Any] = {
            "status": AnalysisRunStatus.FAILED,
            "completed_at": datetime.now(timezone.utc),
        }
        if failure_details is not None:
            values["runtime_metadata"] = {
                **(run.runtime_metadata or {}),
                "failure": failure_details,
            }
        with self._transaction():
            self._analyses.update(run, values)
        return run

    def delete_run(self, organization_id: uuid.UUID, run_id: uuid.UUID) -> None:
        """Deletes a run and its cascading domain results (design delete rules)."""
        run = self._owned_run(organization_id, run_id)
        if run.status == AnalysisRunStatus.PROCESSING:
            raise InvalidStateError("A processing run cannot be deleted")
        with self._transaction():
            self._analyses.delete(run)

    # -- internals ---------------------------------------------------------------------

    def _owned_run(
        self, organization_id: uuid.UUID, run_id: uuid.UUID
    ) -> AnalysisRun:
        run = self.get_run(run_id)
        self._check_ownership(run, "AnalysisRun", organization_id)
        return run

    @staticmethod
    def _validate_transition(run: AnalysisRun, new_status: str) -> None:
        allowed = _RUN_TRANSITIONS.get(run.status, set())
        if new_status not in allowed:
            raise InvalidStateTransitionError("AnalysisRun", run.status, new_status)

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
