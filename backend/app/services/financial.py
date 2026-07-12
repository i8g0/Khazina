"""Financial Data Repository services: upload workflow, imports, data quality."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    DataQualityCheck,
    DataQualitySnapshot,
    FinancialFile,
    ImportRecord,
)
from app.db.models.enums import ImportStatus, ProcessingStatus, UploadSource
from app.repositories import (
    DepartmentRepository,
    FinancialRepository,
    OrganizationRepository,
)
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    InvalidStateTransitionError,
    ResourceNotFoundError,
)

# Approved processing lifecycle (design §4.4): uploads start pending, move
# through processing to completed/failed, and completed files can be promoted
# to ready_for_analysis. Failed files may be retried.
_PROCESSING_TRANSITIONS: dict[str, set[str]] = {
    ProcessingStatus.PENDING: {ProcessingStatus.PROCESSING},
    ProcessingStatus.PROCESSING: {
        ProcessingStatus.COMPLETED,
        ProcessingStatus.FAILED,
    },
    ProcessingStatus.COMPLETED: {ProcessingStatus.READY_FOR_ANALYSIS},
    ProcessingStatus.FAILED: {ProcessingStatus.PROCESSING},
    ProcessingStatus.READY_FOR_ANALYSIS: set(),
}


class FinancialService(BaseService):
    """Business use cases for financial files, import history, and data quality."""

    def __init__(
        self,
        session: Session,
        financial_repository: FinancialRepository,
        organization_repository: OrganizationRepository,
        department_repository: DepartmentRepository,
    ) -> None:
        super().__init__(session)
        self._financials = financial_repository
        self._organizations = organization_repository
        self._departments = department_repository

    # -- upload workflow -------------------------------------------------------

    def register_uploaded_file(
        self,
        organization_id: uuid.UUID,
        *,
        file_name: str,
        upload_source: str = UploadSource.REPOSITORY,
        department_id: uuid.UUID | None = None,
        reporting_period_id: uuid.UUID | None = None,
        storage_path: str | None = None,
        size_bytes: int | None = None,
        size_display: str | None = None,
        mime_type: str | None = None,
        file_metadata: dict[str, Any] | None = None,
    ) -> FinancialFile:
        """Records a new upload in ``pending`` state (upload workflow step 1)."""
        self._require_organization(organization_id)
        file_name = file_name.strip()
        if not file_name:
            raise BusinessValidationError("File name must not be empty")
        if upload_source not in set(UploadSource):
            raise BusinessValidationError(
                f"Unknown upload source '{upload_source}'"
            )
        if size_bytes is not None and size_bytes < 0:
            raise BusinessValidationError("File size must not be negative")
        if department_id is not None:
            self._require_owned_department(organization_id, department_id)
        if reporting_period_id is not None:
            self._require_owned_period(organization_id, reporting_period_id)

        financial_file = FinancialFile(
            organization_id=organization_id,
            department_id=department_id,
            reporting_period_id=reporting_period_id,
            file_name=file_name,
            storage_path=storage_path,
            size_bytes=size_bytes,
            size_display=size_display,
            mime_type=mime_type,
            processing_status=ProcessingStatus.PENDING,
            upload_source=upload_source,
            file_metadata=file_metadata,
        )
        with self._transaction():
            self._financials.create_file(financial_file)
        return financial_file

    def get_file(self, file_id: uuid.UUID) -> FinancialFile:
        return self._found(
            self._financials.get_file(file_id), "FinancialFile", file_id
        )

    def list_files(
        self,
        organization_id: uuid.UUID,
        *,
        processing_status: str | None = None,
        upload_source: str | None = None,
        department_id: uuid.UUID | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[FinancialFile]:
        self._require_organization(organization_id)
        return self._financials.list_files(
            organization_id,
            processing_status=processing_status,
            upload_source=upload_source,
            department_id=department_id,
            limit=limit,
            offset=offset,
        )

    def start_processing(
        self, organization_id: uuid.UUID, file_id: uuid.UUID
    ) -> FinancialFile:
        return self._transition_file(
            organization_id, file_id, ProcessingStatus.PROCESSING
        )

    def complete_processing(
        self,
        organization_id: uuid.UUID,
        file_id: uuid.UUID,
        *,
        record_count: int | None = None,
    ) -> FinancialFile:
        """Marks processing successful and appends a success import record."""
        if record_count is not None and record_count < 0:
            raise BusinessValidationError("Record count must not be negative")
        financial_file = self._owned_file(organization_id, file_id)
        self._validate_transition(financial_file, ProcessingStatus.COMPLETED)

        with self._transaction():
            self._financials.update_file(
                financial_file, {"processing_status": ProcessingStatus.COMPLETED}
            )
            self._financials.add_import_record(
                ImportRecord(
                    financial_file_id=financial_file.id,
                    status=ImportStatus.SUCCESS,
                    record_count=record_count,
                )
            )
        return financial_file

    def fail_processing(
        self,
        organization_id: uuid.UUID,
        file_id: uuid.UUID,
        *,
        error_message: str,
    ) -> FinancialFile:
        """Marks processing failed; the error message is mandatory (design rule)."""
        error_message = error_message.strip()
        if not error_message:
            raise BusinessValidationError(
                "A failed import requires an error message"
            )
        financial_file = self._owned_file(organization_id, file_id)
        self._validate_transition(financial_file, ProcessingStatus.FAILED)

        with self._transaction():
            self._financials.update_file(
                financial_file, {"processing_status": ProcessingStatus.FAILED}
            )
            self._financials.add_import_record(
                ImportRecord(
                    financial_file_id=financial_file.id,
                    status=ImportStatus.FAILED,
                    error_message=error_message,
                )
            )
        return financial_file

    def mark_ready_for_analysis(
        self, organization_id: uuid.UUID, file_id: uuid.UUID
    ) -> FinancialFile:
        return self._transition_file(
            organization_id, file_id, ProcessingStatus.READY_FOR_ANALYSIS
        )

    def delete_file(self, organization_id: uuid.UUID, file_id: uuid.UUID) -> None:
        """Deletes a file; files referenced by analyses are protected (FK RESTRICT)."""
        financial_file = self._owned_file(organization_id, file_id)
        with self._transaction():
            self._financials.delete_file(financial_file)

    # -- import history ----------------------------------------------------------

    def list_import_records(
        self,
        organization_id: uuid.UUID,
        file_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ImportRecord]:
        self._owned_file(organization_id, file_id)
        return self._financials.list_import_records(
            file_id, limit=limit, offset=offset
        )

    # -- data quality ---------------------------------------------------------------

    def record_quality_snapshot(
        self,
        organization_id: uuid.UUID,
        *,
        overall_score: float | None = None,
        reporting_period_id: uuid.UUID | None = None,
        checks: list[dict[str, Any]] | None = None,
    ) -> DataQualitySnapshot:
        """Appends a new quality snapshot with its checks (latest supersedes display)."""
        self._require_organization(organization_id)
        if overall_score is not None and not 0 <= overall_score <= 100:
            raise BusinessValidationError(
                "Overall quality score must be between 0 and 100"
            )
        if reporting_period_id is not None:
            self._require_owned_period(organization_id, reporting_period_id)

        check_rows: list[DataQualityCheck] = []
        for order, check in enumerate(checks or []):
            result_percent = check.get("result_percent")
            if result_percent is None or not 0 <= result_percent <= 100:
                raise BusinessValidationError(
                    "Each quality check requires a result_percent between 0 and 100"
                )
            check_name = str(check.get("check_name", "")).strip()
            if not check_name:
                raise BusinessValidationError(
                    "Each quality check requires a non-empty check_name"
                )
            check_rows.append(
                DataQualityCheck(
                    check_name=check_name,
                    result_percent=result_percent,
                    details=check.get("details"),
                    display_order=check.get("display_order", order),
                )
            )

        snapshot = DataQualitySnapshot(
            organization_id=organization_id,
            reporting_period_id=reporting_period_id,
            overall_score=overall_score,
        )
        with self._transaction():
            self._financials.create_snapshot(snapshot)
            for row in check_rows:
                row.snapshot_id = snapshot.id
            if check_rows:
                self._financials.add_checks(check_rows)
        return snapshot

    def get_latest_quality_snapshot(
        self,
        organization_id: uuid.UUID,
        *,
        reporting_period_id: uuid.UUID | None = None,
    ) -> DataQualitySnapshot | None:
        self._require_organization(organization_id)
        return self._financials.get_latest_snapshot(
            organization_id, reporting_period_id=reporting_period_id
        )

    def list_quality_checks(
        self, organization_id: uuid.UUID, snapshot_id: uuid.UUID
    ) -> list[DataQualityCheck]:
        snapshot = self._found(
            self._financials.get_snapshot(snapshot_id),
            "DataQualitySnapshot",
            snapshot_id,
        )
        self._check_ownership(snapshot, "DataQualitySnapshot", organization_id)
        return self._financials.list_checks(snapshot_id)

    # -- internals ---------------------------------------------------------------------

    def _owned_file(
        self, organization_id: uuid.UUID, file_id: uuid.UUID
    ) -> FinancialFile:
        financial_file = self.get_file(file_id)
        self._check_ownership(financial_file, "FinancialFile", organization_id)
        return financial_file

    def _transition_file(
        self, organization_id: uuid.UUID, file_id: uuid.UUID, new_status: str
    ) -> FinancialFile:
        financial_file = self._owned_file(organization_id, file_id)
        self._validate_transition(financial_file, new_status)
        with self._transaction():
            self._financials.update_file(
                financial_file, {"processing_status": new_status}
            )
        return financial_file

    @staticmethod
    def _validate_transition(financial_file: FinancialFile, new_status: str) -> None:
        allowed = _PROCESSING_TRANSITIONS.get(financial_file.processing_status, set())
        if new_status not in allowed:
            raise InvalidStateTransitionError(
                "FinancialFile", financial_file.processing_status, new_status
            )

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)

    def _require_owned_department(
        self, organization_id: uuid.UUID, department_id: uuid.UUID
    ) -> None:
        department = self._departments.get(department_id)
        if department is None:
            raise ResourceNotFoundError("Department", department_id)
        self._check_ownership(department, "Department", organization_id)

    def _require_owned_period(
        self, organization_id: uuid.UUID, period_id: uuid.UUID
    ) -> None:
        period = self._organizations.get_reporting_period(period_id)
        if period is None:
            raise ResourceNotFoundError("ReportingPeriod", period_id)
        self._check_ownership(period, "ReportingPeriod", organization_id)
