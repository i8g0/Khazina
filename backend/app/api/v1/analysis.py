"""Analysis run REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import AnalysisServiceDep, PaginationDep
from app.api.permissions import RequireOrgAdmin, RequireOrgExecutive, require_org_role
from app.db.models.enums import UserRole
from app.schemas.analysis import (
    AnalysisRunCreate,
    AnalysisRunResponse,
    FailAnalysisRunRequest,
)
from app.schemas.response import ApiResponse, success_response

router = APIRouter(
    prefix="/organizations/{organization_id}/analysis-runs",
    tags=["analysis"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.post(
    "",
    response_model=ApiResponse[AnalysisRunResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create analysis run",
)
def create_analysis_run(
    organization_id: UUID,
    body: AnalysisRunCreate,
    service: AnalysisServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[AnalysisRunResponse]:
    run = service.create_run(
        organization_id,
        analysis_type=body.analysis_type,
        title=body.title,
        source_file_id=body.source_file_id,
        source_snapshot_id=body.source_snapshot_id,
        reporting_period_id=body.reporting_period_id,
        runtime_metadata=body.runtime_metadata,
    )
    return success_response(
        data=AnalysisRunResponse.model_validate(run),
        message="Analysis run created",
    )


@router.get(
    "",
    response_model=ApiResponse[list[AnalysisRunResponse]],
    summary="List analysis runs",
)
def list_analysis_runs(
    organization_id: UUID,
    service: AnalysisServiceDep,
    pagination: PaginationDep,
    analysis_type: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
) -> ApiResponse[list[AnalysisRunResponse]]:
    runs = service.list_runs(
        organization_id,
        analysis_type=analysis_type,
        status=status_filter,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[AnalysisRunResponse.model_validate(r) for r in runs],
        message="Analysis runs retrieved",
    )


@router.get(
    "/recent-completed",
    response_model=ApiResponse[list[AnalysisRunResponse]],
    summary="List recently completed analysis runs",
)
def list_recent_completed_runs(
    organization_id: UUID,
    service: AnalysisServiceDep,
    limit: int = Query(10, ge=1, le=100),
) -> ApiResponse[list[AnalysisRunResponse]]:
    runs = service.list_recent_completed(organization_id, limit=limit)
    return success_response(
        data=[AnalysisRunResponse.model_validate(r) for r in runs],
        message="Recent completed runs retrieved",
    )


@router.get(
    "/{run_id}",
    response_model=ApiResponse[AnalysisRunResponse],
    summary="Get analysis run by ID",
)
def get_analysis_run(
    organization_id: UUID,
    run_id: UUID,
    service: AnalysisServiceDep,
) -> ApiResponse[AnalysisRunResponse]:
    run = service.get_run(run_id)
    return success_response(
        data=AnalysisRunResponse.model_validate(run),
        message="Analysis run retrieved",
    )


@router.post(
    "/{run_id}/start",
    response_model=ApiResponse[AnalysisRunResponse],
    summary="Start analysis run",
)
def start_analysis_run(
    organization_id: UUID,
    run_id: UUID,
    service: AnalysisServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[AnalysisRunResponse]:
    run = service.start_run(organization_id, run_id)
    return success_response(
        data=AnalysisRunResponse.model_validate(run),
        message="Analysis run started",
    )


@router.post(
    "/{run_id}/complete",
    response_model=ApiResponse[AnalysisRunResponse],
    summary="Complete analysis run",
)
def complete_analysis_run(
    organization_id: UUID,
    run_id: UUID,
    service: AnalysisServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[AnalysisRunResponse]:
    run = service.complete_run(organization_id, run_id)
    return success_response(
        data=AnalysisRunResponse.model_validate(run),
        message="Analysis run completed",
    )


@router.post(
    "/{run_id}/fail",
    response_model=ApiResponse[AnalysisRunResponse],
    summary="Fail analysis run",
)
def fail_analysis_run(
    organization_id: UUID,
    run_id: UUID,
    body: FailAnalysisRunRequest,
    service: AnalysisServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[AnalysisRunResponse]:
    run = service.fail_run(
        organization_id, run_id, failure_details=body.failure_details
    )
    return success_response(
        data=AnalysisRunResponse.model_validate(run),
        message="Analysis run failed",
    )


@router.delete(
    "/{run_id}",
    response_model=ApiResponse[None],
    summary="Delete analysis run",
)
def delete_analysis_run(
    organization_id: UUID,
    run_id: UUID,
    service: AnalysisServiceDep,
    _current_user: RequireOrgAdmin,
) -> ApiResponse[None]:
    service.delete_run(organization_id, run_id)
    return success_response(data=None, message="Analysis run deleted")
