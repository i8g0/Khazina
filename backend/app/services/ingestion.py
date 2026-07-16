"""Ingestion service — upload, Bronze storage, and Silver snapshot creation."""

from __future__ import annotations

import logging
import mimetypes
import time
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    DataQualityCheck,
    DataQualitySnapshot,
    FinancialFile,
    FinancialSnapshot,
    ImportRecord,
)
from app.db.models.enums import ImportStatus, ProcessingStatus, UploadSource
from app.ingestion.constants import PARSER_VERSION, SCHEMA_VERSION
from app.ingestion.exceptions import IngestionError, ParseError, ValidationFailure
from app.ingestion.orchestrator import IngestionOrchestrator
from app.ingestion.storage import BronzeStorage
from app.core.logging import get_logger
from app.observability.errors import classify_exception
from app.observability.persistence import file_metadata_with_timeline
from app.observability.pipeline import PipelineStage, PipelineTimeline
from app.observability.structured_log import log_pipeline_event
from app.repositories import (
    DepartmentRepository,
    FinancialRepository,
    FinancialSnapshotRepository,
    OrganizationRepository,
)
from app.services.base import BaseService
from app.services.exceptions import BusinessValidationError, ResourceNotFoundError
from app.services.financial import _PROCESSING_TRANSITIONS

_PROCESSING = ProcessingStatus.PROCESSING
_COMPLETED = ProcessingStatus.COMPLETED
_FAILED = ProcessingStatus.FAILED
_READY = ProcessingStatus.READY_FOR_ANALYSIS
_PENDING = ProcessingStatus.PENDING

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class UploadIngestionOutcome:
    financial_file: FinancialFile
    financial_snapshot: FinancialSnapshot | None
    quality_snapshot: DataQualitySnapshot | None
    import_record: ImportRecord | None


class IngestionService(BaseService):
    """Orchestrates Bronze-to-Silver ingestion per Sprint 6.2 / ADR-010."""

    def __init__(
        self,
        session: Session,
        financial_repository: FinancialRepository,
        snapshot_repository: FinancialSnapshotRepository,
        organization_repository: OrganizationRepository,
        department_repository: DepartmentRepository,
        bronze_storage: BronzeStorage,
        orchestrator: IngestionOrchestrator | None = None,
        max_upload_size_bytes: int = 10_485_760,
    ) -> None:
        super().__init__(session)
        self._financials = financial_repository
        self._snapshots = snapshot_repository
        self._organizations = organization_repository
        self._departments = department_repository
        self._bronze = bronze_storage
        self._orchestrator = orchestrator or IngestionOrchestrator()
        self._max_upload_size = max_upload_size_bytes

    def upload_and_ingest(
        self,
        organization_id: uuid.UUID,
        *,
        file_name: str,
        content: bytes,
        upload_source: str = UploadSource.REPOSITORY,
        department_id: uuid.UUID | None = None,
        reporting_period_id: uuid.UUID | None = None,
        mime_type: str | None = None,
    ) -> UploadIngestionOutcome:
        org_key = str(organization_id)
        timeline = PipelineTimeline(organization_id=org_key)
        pipeline_started = time.perf_counter()
        timeline.start_stage(PipelineStage.UPLOAD_STARTED)
        log_pipeline_event(
            logger,
            "pipeline_stage",
            stage=PipelineStage.UPLOAD_STARTED.value,
            status="started",
            organization_id=org_key,
            message=file_name,
        )

        try:
            self._validate_upload_request(
                organization_id,
                file_name=file_name,
                content=content,
                upload_source=upload_source,
                department_id=department_id,
                reporting_period_id=reporting_period_id,
            )
            storage_path, size_bytes = self._bronze.save(
                organization_id, file_name, content
            )
            size_display = BronzeStorage.format_size_display(size_bytes)
            resolved_mime = mime_type or mimetypes.guess_type(file_name)[0]

            financial_file = FinancialFile(
                organization_id=organization_id,
                department_id=department_id,
                reporting_period_id=reporting_period_id,
                file_name=file_name.strip(),
                storage_path=storage_path,
                size_bytes=size_bytes,
                size_display=size_display,
                mime_type=resolved_mime,
                processing_status=_PENDING,
                upload_source=upload_source,
            )

            with self._transaction():
                self._financials.create_file(financial_file)
                self._transition(financial_file, _PROCESSING)
                processing_record = ImportRecord(
                    financial_file_id=financial_file.id,
                    status=ImportStatus.PROCESSING,
                )
                self._financials.add_import_record(processing_record)

            timeline.file_id = str(financial_file.id)
            try:
                ingestion = self._orchestrator.run(
                    storage_path,
                    file_name,
                    timeline=timeline,
                )
            except (ParseError, ValidationFailure, IngestionError) as exc:
                category = classify_exception(exc)
                timeline.fail_stage(PipelineStage.UPLOAD_COMPLETED, exc)
                log_pipeline_event(
                    logger,
                    "pipeline_stage",
                    level=logging.WARNING,
                    stage=PipelineStage.UPLOAD_COMPLETED.value,
                    status="failed",
                    organization_id=org_key,
                    file_id=str(financial_file.id),
                    error_category=category,
                    duration_ms=round((time.perf_counter() - pipeline_started) * 1000, 2),
                    message=str(exc),
                )
                return self._finalize_failure(
                    organization_id,
                    financial_file.id,
                    error_message=str(exc),
                    timeline=timeline.to_list(),
                )

            timeline.start_stage(PipelineStage.SNAPSHOT_CREATED)
            outcome = self._finalize_success(
                organization_id,
                financial_file.id,
                ingestion_result=ingestion,
                timeline=timeline,
            )
            timeline.complete_stage(PipelineStage.SNAPSHOT_CREATED)
            timeline.complete_stage(PipelineStage.UPLOAD_COMPLETED)
            duration_ms = round((time.perf_counter() - pipeline_started) * 1000, 2)
            log_pipeline_event(
                logger,
                "pipeline_stage",
                stage=PipelineStage.UPLOAD_COMPLETED.value,
                status="completed",
                organization_id=org_key,
                file_id=str(outcome.financial_file.id),
                snapshot_id=(
                    str(outcome.financial_snapshot.id)
                    if outcome.financial_snapshot
                    else None
                ),
                duration_ms=duration_ms,
                message=file_name,
            )
            return outcome
        except Exception as exc:
            category = classify_exception(exc)
            timeline.fail_stage(PipelineStage.UPLOAD_COMPLETED, exc)
            log_pipeline_event(
                logger,
                "pipeline_stage",
                level=logging.ERROR,
                stage=PipelineStage.UPLOAD_COMPLETED.value,
                status="failed",
                organization_id=org_key,
                error_category=category,
                duration_ms=round((time.perf_counter() - pipeline_started) * 1000, 2),
                message=str(exc),
            )
            raise

    def get_snapshot(
        self, organization_id: uuid.UUID, snapshot_id: uuid.UUID
    ) -> FinancialSnapshot:
        snapshot = self._found(
            self._snapshots.get_snapshot(snapshot_id),
            "FinancialSnapshot",
            snapshot_id,
        )
        self._check_ownership(snapshot, "FinancialSnapshot", organization_id)
        return snapshot

    def list_snapshots_for_file(
        self,
        organization_id: uuid.UUID,
        file_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[FinancialSnapshot]:
        financial_file = self._owned_file(organization_id, file_id)
        return self._snapshots.list_snapshots_for_file(
            financial_file.id, limit=limit, offset=offset
        )

    def get_latest_snapshot_for_file(
        self, organization_id: uuid.UUID, file_id: uuid.UUID
    ) -> FinancialSnapshot | None:
        financial_file = self._owned_file(organization_id, file_id)
        return self._snapshots.get_latest_snapshot_for_file(financial_file.id)

    def _finalize_success(
        self,
        organization_id: uuid.UUID,
        file_id: uuid.UUID,
        *,
        ingestion_result: Any,
        timeline: PipelineTimeline | None = None,
    ) -> UploadIngestionOutcome:
        financial_file = self._owned_file(organization_id, file_id)
        snapshot_version = self._snapshots.next_snapshot_version(financial_file.id)

        with self._transaction():
            self._transition(financial_file, _COMPLETED)
            success_record = ImportRecord(
                financial_file_id=financial_file.id,
                status=ImportStatus.SUCCESS,
                record_count=ingestion_result.record_count,
            )
            self._financials.add_import_record(success_record)

            financial_snapshot = FinancialSnapshot(
                financial_file_id=financial_file.id,
                import_record_id=success_record.id,
                organization_id=organization_id,
                reporting_period_id=financial_file.reporting_period_id,
                snapshot_version=snapshot_version,
                parser_version=PARSER_VERSION,
                schema_version=SCHEMA_VERSION,
                record_count=ingestion_result.record_count,
                payload=ingestion_result.dataset.to_payload(),
            )
            self._snapshots.create_snapshot(financial_snapshot)

            self._financials.update_file(
                financial_file,
                {
                    "file_metadata": {
                        **ingestion_result.parse_metadata.to_dict(),
                        **(
                            {"pipeline_timeline": timeline.to_list()}
                            if timeline is not None
                            else {}
                        ),
                    }
                },
            )
            self._transition(financial_file, _READY)

            quality_snapshot = DataQualitySnapshot(
                organization_id=organization_id,
                reporting_period_id=financial_file.reporting_period_id,
                overall_score=ingestion_result.quality.overall_score,
            )
            self._financials.create_snapshot(quality_snapshot)
            quality_checks = [
                DataQualityCheck(
                    snapshot_id=quality_snapshot.id,
                    check_name=check.check_name,
                    result_percent=check.result_percent,
                    details=check.details,
                    display_order=check.display_order,
                )
                for check in ingestion_result.quality.checks
            ]
            if quality_checks:
                self._financials.add_checks(quality_checks)

        refreshed_file = self._owned_file(organization_id, file_id)
        return UploadIngestionOutcome(
            financial_file=refreshed_file,
            financial_snapshot=financial_snapshot,
            quality_snapshot=quality_snapshot,
            import_record=success_record,
        )

    def _finalize_failure(
        self,
        organization_id: uuid.UUID,
        file_id: uuid.UUID,
        *,
        error_message: str,
        timeline: list[dict[str, Any]] | None = None,
    ) -> UploadIngestionOutcome:
        financial_file = self._owned_file(organization_id, file_id)
        with self._transaction():
            self._transition(financial_file, _FAILED)
            failed_record = ImportRecord(
                financial_file_id=financial_file.id,
                status=ImportStatus.FAILED,
                error_message=error_message.strip(),
            )
            self._financials.add_import_record(failed_record)
            if timeline is not None:
                self._financials.update_file(
                    financial_file,
                    {
                        "file_metadata": file_metadata_with_timeline(
                            financial_file,
                            timeline,
                        )
                    },
                )
        refreshed_file = self._owned_file(organization_id, file_id)
        return UploadIngestionOutcome(
            financial_file=refreshed_file,
            financial_snapshot=None,
            quality_snapshot=None,
            import_record=failed_record,
        )

    def _validate_upload_request(
        self,
        organization_id: uuid.UUID,
        *,
        file_name: str,
        content: bytes,
        upload_source: str,
        department_id: uuid.UUID | None,
        reporting_period_id: uuid.UUID | None,
    ) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
        file_name = file_name.strip()
        if not file_name:
            raise BusinessValidationError("File name must not be empty")
        if not content:
            raise BusinessValidationError("Uploaded file is empty")
        if len(content) > self._max_upload_size:
            raise BusinessValidationError(
                f"File exceeds maximum upload size of {self._max_upload_size} bytes"
            )
        if upload_source not in set(UploadSource):
            raise BusinessValidationError(f"Unknown upload source '{upload_source}'")
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

    def _owned_file(
        self, organization_id: uuid.UUID, file_id: uuid.UUID
    ) -> FinancialFile:
        financial_file = self._found(
            self._financials.get_file(file_id), "FinancialFile", file_id
        )
        self._check_ownership(financial_file, "FinancialFile", organization_id)
        return financial_file

    def _transition(self, financial_file: FinancialFile, new_status: str) -> None:
        allowed = _PROCESSING_TRANSITIONS.get(financial_file.processing_status, set())
        if new_status not in allowed:
            from app.services.exceptions import InvalidStateTransitionError

            raise InvalidStateTransitionError(
                "FinancialFile", financial_file.processing_status, new_status
            )
        self._financials.update_file(
            financial_file, {"processing_status": new_status}
        )
