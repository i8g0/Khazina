"""Financial data repository REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.api.deps import FinancialServiceDep, IngestionServiceDep, PaginationDep
from app.api.permissions import RequireOrgAdmin, RequireOrgExecutive, require_org_role
from app.db.models.enums import UploadSource, UserRole
from app.schemas.financial import (
    CompleteProcessingRequest,
    DataQualityCheckResponse,
    DataQualitySnapshotCreate,
    DataQualitySnapshotResponse,
    FailProcessingRequest,
    FinancialFileCreate,
    FinancialFileResponse,
    ImportRecordResponse,
)
from app.schemas.response import ApiResponse, success_response
from app.schemas.snapshot import (
    FinancialSnapshotDetailResponse,
    FinancialSnapshotResponse,
    UploadIngestionResponse,
)

router = APIRouter(
    prefix="/organizations/{organization_id}",
    tags=["financial"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.post(
    "/financial-files",
    response_model=ApiResponse[FinancialFileResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register uploaded financial file",
)
def register_financial_file(
    organization_id: UUID,
    body: FinancialFileCreate,
    service: FinancialServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[FinancialFileResponse]:
    file = service.register_uploaded_file(
        organization_id,
        file_name=body.file_name,
        upload_source=body.upload_source,
        department_id=body.department_id,
        reporting_period_id=body.reporting_period_id,
        storage_path=body.storage_path,
        size_bytes=body.size_bytes,
        size_display=body.size_display,
        mime_type=body.mime_type,
        file_metadata=body.file_metadata,
    )
    return success_response(
        data=FinancialFileResponse.model_validate(file),
        message="Financial file registered",
    )


@router.post(
    "/financial-files/upload",
    response_model=ApiResponse[UploadIngestionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest financial file",
)
async def upload_financial_file(
    organization_id: UUID,
    ingestion_service: IngestionServiceDep,
    _current_user: RequireOrgExecutive,
    upload: UploadFile = File(...),
    upload_source: str = Form(UploadSource.REPOSITORY),
    department_id: UUID | None = Form(None),
    reporting_period_id: UUID | None = Form(None),
) -> ApiResponse[UploadIngestionResponse]:
    content = await upload.read()
    outcome = ingestion_service.upload_and_ingest(
        organization_id,
        file_name=upload.filename or "upload.xlsx",
        content=content,
        upload_source=upload_source,
        department_id=department_id,
        reporting_period_id=reporting_period_id,
        mime_type=upload.content_type,
    )
    snapshot_response = (
        FinancialSnapshotResponse.model_validate(outcome.financial_snapshot)
        if outcome.financial_snapshot
        else None
    )
    return success_response(
        data=UploadIngestionResponse(
            financial_file=FinancialFileResponse.model_validate(outcome.financial_file),
            financial_snapshot=snapshot_response,
            quality_snapshot_id=(
                outcome.quality_snapshot.id if outcome.quality_snapshot else None
            ),
            import_record_id=(
                outcome.import_record.id if outcome.import_record else None
            ),
        ),
        message=(
            "Financial file ingested and ready for analysis"
            if outcome.financial_snapshot
            else "Financial file ingestion failed"
        ),
    )


@router.get(
    "/financial-files",
    response_model=ApiResponse[list[FinancialFileResponse]],
    summary="List financial files",
)
def list_financial_files(
    organization_id: UUID,
    service: FinancialServiceDep,
    pagination: PaginationDep,
    processing_status: str | None = Query(None),
    upload_source: str | None = Query(None),
    department_id: UUID | None = Query(None),
) -> ApiResponse[list[FinancialFileResponse]]:
    files = service.list_files(
        organization_id,
        processing_status=processing_status,
        upload_source=upload_source,
        department_id=department_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[FinancialFileResponse.model_validate(f) for f in files],
        message="Financial files retrieved",
    )


@router.get(
    "/financial-files/{file_id}",
    response_model=ApiResponse[FinancialFileResponse],
    summary="Get financial file by ID",
)
def get_financial_file(
    organization_id: UUID,
    file_id: UUID,
    service: FinancialServiceDep,
) -> ApiResponse[FinancialFileResponse]:
    file = service.get_organization_file(organization_id, file_id)
    return success_response(
        data=FinancialFileResponse.model_validate(file),
        message="Financial file retrieved",
    )


@router.post(
    "/financial-files/{file_id}/start-processing",
    response_model=ApiResponse[FinancialFileResponse],
    summary="Start file processing",
)
def start_processing(
    organization_id: UUID,
    file_id: UUID,
    service: FinancialServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[FinancialFileResponse]:
    file = service.start_processing(organization_id, file_id)
    return success_response(
        data=FinancialFileResponse.model_validate(file),
        message="Processing started",
    )


@router.post(
    "/financial-files/{file_id}/complete-processing",
    response_model=ApiResponse[FinancialFileResponse],
    summary="Complete file processing",
)
def complete_processing(
    organization_id: UUID,
    file_id: UUID,
    body: CompleteProcessingRequest,
    service: FinancialServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[FinancialFileResponse]:
    file = service.complete_processing(
        organization_id, file_id, record_count=body.record_count
    )
    return success_response(
        data=FinancialFileResponse.model_validate(file),
        message="Processing completed",
    )


@router.post(
    "/financial-files/{file_id}/fail-processing",
    response_model=ApiResponse[FinancialFileResponse],
    summary="Mark file processing as failed",
)
def fail_processing(
    organization_id: UUID,
    file_id: UUID,
    body: FailProcessingRequest,
    service: FinancialServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[FinancialFileResponse]:
    file = service.fail_processing(
        organization_id, file_id, error_message=body.error_message
    )
    return success_response(
        data=FinancialFileResponse.model_validate(file),
        message="Processing failed",
    )


@router.post(
    "/financial-files/{file_id}/ready-for-analysis",
    response_model=ApiResponse[FinancialFileResponse],
    summary="Mark file ready for analysis",
)
def mark_ready_for_analysis(
    organization_id: UUID,
    file_id: UUID,
    service: FinancialServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[FinancialFileResponse]:
    file = service.mark_ready_for_analysis(organization_id, file_id)
    return success_response(
        data=FinancialFileResponse.model_validate(file),
        message="File marked ready for analysis",
    )


@router.delete(
    "/financial-files/{file_id}",
    response_model=ApiResponse[None],
    summary="Delete financial file",
)
def delete_financial_file(
    organization_id: UUID,
    file_id: UUID,
    service: FinancialServiceDep,
    _current_user: RequireOrgAdmin,
) -> ApiResponse[None]:
    service.delete_file(organization_id, file_id)
    return success_response(data=None, message="Financial file deleted")


@router.get(
    "/financial-files/{file_id}/import-records",
    response_model=ApiResponse[list[ImportRecordResponse]],
    summary="List import records for a file",
)
def list_import_records(
    organization_id: UUID,
    file_id: UUID,
    service: FinancialServiceDep,
    pagination: PaginationDep,
) -> ApiResponse[list[ImportRecordResponse]]:
    records = service.list_import_records(
        organization_id,
        file_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[ImportRecordResponse.model_validate(r) for r in records],
        message="Import records retrieved",
    )


@router.post(
    "/data-quality-snapshots",
    response_model=ApiResponse[DataQualitySnapshotResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Record data quality snapshot",
)
def record_quality_snapshot(
    organization_id: UUID,
    body: DataQualitySnapshotCreate,
    service: FinancialServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[DataQualitySnapshotResponse]:
    checks = [c.model_dump() for c in body.checks] if body.checks else None
    snapshot = service.record_quality_snapshot(
        organization_id,
        overall_score=body.overall_score,
        reporting_period_id=body.reporting_period_id,
        checks=checks,
    )
    return success_response(
        data=DataQualitySnapshotResponse.model_validate(snapshot),
        message="Data quality snapshot recorded",
    )


@router.get(
    "/data-quality-snapshots/latest",
    response_model=ApiResponse[DataQualitySnapshotResponse | None],
    summary="Get latest data quality snapshot",
)
def get_latest_quality_snapshot(
    organization_id: UUID,
    service: FinancialServiceDep,
    reporting_period_id: UUID | None = Query(None),
) -> ApiResponse[DataQualitySnapshotResponse | None]:
    snapshot = service.get_latest_quality_snapshot(
        organization_id, reporting_period_id=reporting_period_id
    )
    data = (
        DataQualitySnapshotResponse.model_validate(snapshot) if snapshot else None
    )
    return success_response(data=data, message="Latest snapshot retrieved")


@router.get(
    "/data-quality-snapshots/{snapshot_id}/checks",
    response_model=ApiResponse[list[DataQualityCheckResponse]],
    summary="List checks for a data quality snapshot",
)
def list_quality_checks(
    organization_id: UUID,
    snapshot_id: UUID,
    service: FinancialServiceDep,
) -> ApiResponse[list[DataQualityCheckResponse]]:
    checks = service.list_quality_checks(organization_id, snapshot_id)
    return success_response(
        data=[DataQualityCheckResponse.model_validate(c) for c in checks],
        message="Quality checks retrieved",
    )


@router.get(
    "/financial-files/{file_id}/snapshots",
    response_model=ApiResponse[list[FinancialSnapshotResponse]],
    summary="List financial snapshots for a file",
)
def list_financial_snapshots(
    organization_id: UUID,
    file_id: UUID,
    ingestion_service: IngestionServiceDep,
    pagination: PaginationDep,
) -> ApiResponse[list[FinancialSnapshotResponse]]:
    snapshots = ingestion_service.list_snapshots_for_file(
        organization_id,
        file_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[FinancialSnapshotResponse.model_validate(s) for s in snapshots],
        message="Financial snapshots retrieved",
    )


@router.get(
    "/financial-files/{file_id}/snapshots/latest",
    response_model=ApiResponse[FinancialSnapshotResponse | None],
    summary="Get latest financial snapshot for a file",
)
def get_latest_financial_snapshot(
    organization_id: UUID,
    file_id: UUID,
    ingestion_service: IngestionServiceDep,
) -> ApiResponse[FinancialSnapshotResponse | None]:
    snapshot = ingestion_service.get_latest_snapshot_for_file(organization_id, file_id)
    data = FinancialSnapshotResponse.model_validate(snapshot) if snapshot else None
    return success_response(data=data, message="Latest financial snapshot retrieved")


@router.get(
    "/financial-snapshots/{snapshot_id}",
    response_model=ApiResponse[FinancialSnapshotDetailResponse],
    summary="Get financial snapshot with payload",
)
def get_financial_snapshot(
    organization_id: UUID,
    snapshot_id: UUID,
    ingestion_service: IngestionServiceDep,
) -> ApiResponse[FinancialSnapshotDetailResponse]:
    snapshot = ingestion_service.get_snapshot(organization_id, snapshot_id)
    return success_response(
        data=FinancialSnapshotDetailResponse.model_validate(snapshot),
        message="Financial snapshot retrieved",
    )
