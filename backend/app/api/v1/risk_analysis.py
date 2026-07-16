"""Risk analysis REST endpoints (Sprint 9.3)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import PaginationDep, RiskAnalysisServiceDep
from app.api.permissions import RequireOrgExecutive, require_org_role
from app.db.models.enums import UserRole
from app.schemas.analysis import AnalysisRunResponse
from app.schemas.response import ApiResponse, success_response
from app.schemas.risk_analysis import (
    RiskAnalysisExecuteRequest,
    RiskAnalysisExecuteResponse,
    RiskAnalysisResultResponse,
    RiskAnalysisResultSummary,
    RiskAnalysisRunDetailResponse,
    RiskFindingResponse,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/risk-analyses",
    tags=["risk-analysis"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.post(
    "/execute",
    response_model=ApiResponse[RiskAnalysisExecuteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Execute risk analysis on a financial snapshot",
)
def execute_risk_analysis(
    organization_id: UUID,
    body: RiskAnalysisExecuteRequest,
    service: RiskAnalysisServiceDep,
    current_user: RequireOrgExecutive,
) -> ApiResponse[RiskAnalysisExecuteResponse]:
    outcome = service.execute(
        organization_id,
        title=body.title,
        source_file_id=body.source_file_id,
        source_snapshot_id=body.source_snapshot_id,
        snapshot_version=body.snapshot_version,
        reporting_period_id=body.reporting_period_id,
        initiating_user_id=current_user.id,
    )
    facts = outcome.decision_outcome.facts_contract
    summary = service.build_result_summary(outcome.result)
    assert summary is not None
    return success_response(
        data=RiskAnalysisExecuteResponse(
            analysis_run=AnalysisRunResponse.model_validate(outcome.analysis_run),
            result_summary=RiskAnalysisResultSummary.model_validate(summary),
            facts_contract_version=facts.contract_version,
            engine_id=facts.engine_id,
            engine_version=facts.engine_version,
            snapshot_id=outcome.decision_outcome.snapshot.id,
            snapshot_version=outcome.decision_outcome.snapshot.snapshot_version,
        ),
        message="Risk analysis executed",
    )


@router.get(
    "",
    response_model=ApiResponse[list[AnalysisRunResponse]],
    summary="List risk analysis runs",
)
def list_risk_analyses(
    organization_id: UUID,
    service: RiskAnalysisServiceDep,
    pagination: PaginationDep,
    status_filter: str | None = Query(None, alias="status"),
) -> ApiResponse[list[AnalysisRunResponse]]:
    runs = service.list_runs(
        organization_id,
        status=status_filter,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[AnalysisRunResponse.model_validate(run) for run in runs],
        message="Risk analyses retrieved",
    )


@router.get(
    "/{run_id}",
    response_model=ApiResponse[RiskAnalysisRunDetailResponse],
    summary="Get risk analysis run detail",
)
def get_risk_analysis(
    organization_id: UUID,
    run_id: UUID,
    service: RiskAnalysisServiceDep,
) -> ApiResponse[RiskAnalysisRunDetailResponse]:
    run, result = service.get_run_detail(organization_id, run_id)
    summary = service.build_result_summary(result)
    return success_response(
        data=RiskAnalysisRunDetailResponse(
            analysis_run=AnalysisRunResponse.model_validate(run),
            result_summary=(
                RiskAnalysisResultSummary.model_validate(summary)
                if summary is not None
                else None
            ),
        ),
        message="Risk analysis retrieved",
    )


@router.get(
    "/{run_id}/result",
    response_model=ApiResponse[RiskAnalysisResultResponse],
    summary="Get full risk analysis result aggregates",
)
def get_risk_analysis_result(
    organization_id: UUID,
    run_id: UUID,
    service: RiskAnalysisServiceDep,
) -> ApiResponse[RiskAnalysisResultResponse]:
    result = service.get_result(organization_id, run_id)
    return success_response(
        data=RiskAnalysisResultResponse.model_validate(result),
        message="Risk analysis result retrieved",
    )


@router.get(
    "/{run_id}/findings",
    response_model=ApiResponse[list[RiskFindingResponse]],
    summary="List findings for a risk analysis run",
)
def list_risk_findings(
    organization_id: UUID,
    run_id: UUID,
    service: RiskAnalysisServiceDep,
    pagination: PaginationDep,
    priority: str | None = Query(None),
    category_code: str | None = Query(None),
    finding_status: str | None = Query(None),
) -> ApiResponse[list[RiskFindingResponse]]:
    findings = service.list_findings(
        organization_id,
        run_id,
        priority=priority,
        category_code=category_code,
        finding_status=finding_status,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[RiskFindingResponse.model_validate(item) for item in findings],
        message="Risk findings retrieved",
    )


@router.get(
    "/{run_id}/findings/{finding_id}",
    response_model=ApiResponse[RiskFindingResponse],
    summary="Get a single risk finding detail",
)
def get_risk_finding(
    organization_id: UUID,
    run_id: UUID,
    finding_id: UUID,
    service: RiskAnalysisServiceDep,
) -> ApiResponse[RiskFindingResponse]:
    finding = service.get_finding(organization_id, run_id, finding_id)
    return success_response(
        data=RiskFindingResponse.model_validate(finding),
        message="Risk finding retrieved",
    )
