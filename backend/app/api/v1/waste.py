"""Waste analysis REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import PaginationDep, WasteServiceDep
from app.schemas.response import ApiResponse, success_response
from app.schemas.waste import (
    WasteAnalysisResultResponse,
    WasteCategoryBreakdownResponse,
    WasteResultCreate,
    WasteTrendPointResponse,
    WasteTrendPointUpsert,
    WasteVendorFindingResponse,
)

router = APIRouter(
    prefix="/organizations/{organization_id}",
    tags=["waste"],
)


@router.post(
    "/analysis-runs/{run_id}/waste/result",
    response_model=ApiResponse[WasteAnalysisResultResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Record waste analysis result",
)
def record_waste_result(
    organization_id: UUID,
    run_id: UUID,
    body: WasteResultCreate,
    service: WasteServiceDep,
) -> ApiResponse[WasteAnalysisResultResponse]:
    breakdowns = (
        [b.model_dump() for b in body.category_breakdowns]
        if body.category_breakdowns
        else None
    )
    findings = (
        [f.model_dump() for f in body.vendor_findings]
        if body.vendor_findings
        else None
    )
    result = service.record_result(
        organization_id,
        run_id,
        total_waste_amount=body.total_waste_amount,
        waste_percentage=body.waste_percentage,
        top_category_name=body.top_category_name,
        top_category_percentage=body.top_category_percentage,
        potential_savings_amount=body.potential_savings_amount,
        active_savings_opportunities=body.active_savings_opportunities,
        category_breakdowns=breakdowns,
        vendor_findings=findings,
    )
    return success_response(
        data=WasteAnalysisResultResponse.model_validate(result),
        message="Waste result recorded",
    )


@router.get(
    "/analysis-runs/{run_id}/waste/result",
    response_model=ApiResponse[WasteAnalysisResultResponse],
    summary="Get waste analysis result for a run",
)
def get_waste_result(
    organization_id: UUID,
    run_id: UUID,
    service: WasteServiceDep,
) -> ApiResponse[WasteAnalysisResultResponse]:
    result = service.get_result_for_run(organization_id, run_id)
    return success_response(
        data=WasteAnalysisResultResponse.model_validate(result),
        message="Waste result retrieved",
    )


@router.get(
    "/analysis-runs/{run_id}/waste/category-breakdowns",
    response_model=ApiResponse[list[WasteCategoryBreakdownResponse]],
    summary="List waste category breakdowns",
)
def list_category_breakdowns(
    organization_id: UUID,
    run_id: UUID,
    service: WasteServiceDep,
    department_id: UUID | None = Query(None),
) -> ApiResponse[list[WasteCategoryBreakdownResponse]]:
    breakdowns = service.list_category_breakdowns(
        organization_id, run_id, department_id=department_id
    )
    return success_response(
        data=[WasteCategoryBreakdownResponse.model_validate(b) for b in breakdowns],
        message="Category breakdowns retrieved",
    )


@router.get(
    "/analysis-runs/{run_id}/waste/vendor-findings",
    response_model=ApiResponse[list[WasteVendorFindingResponse]],
    summary="List waste vendor findings",
)
def list_vendor_findings(
    organization_id: UUID,
    run_id: UUID,
    service: WasteServiceDep,
    pagination: PaginationDep,
) -> ApiResponse[list[WasteVendorFindingResponse]]:
    findings = service.list_vendor_findings(
        organization_id,
        run_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[WasteVendorFindingResponse.model_validate(f) for f in findings],
        message="Vendor findings retrieved",
    )


@router.post(
    "/waste/trend-points",
    response_model=ApiResponse[WasteTrendPointResponse],
    summary="Create or update waste trend point",
)
def upsert_trend_point(
    organization_id: UUID,
    body: WasteTrendPointUpsert,
    service: WasteServiceDep,
) -> ApiResponse[WasteTrendPointResponse]:
    point = service.upsert_trend_point(
        organization_id,
        month_label=body.month_label,
        month_order=body.month_order,
        waste_amount=body.waste_amount,
        reporting_period_id=body.reporting_period_id,
    )
    return success_response(
        data=WasteTrendPointResponse.model_validate(point),
        message="Trend point upserted",
    )


@router.get(
    "/waste/trend-points",
    response_model=ApiResponse[list[WasteTrendPointResponse]],
    summary="List waste trend points",
)
def list_trend_points(
    organization_id: UUID,
    service: WasteServiceDep,
    reporting_period_id: UUID | None = Query(None),
) -> ApiResponse[list[WasteTrendPointResponse]]:
    points = service.list_trend_points(
        organization_id, reporting_period_id=reporting_period_id
    )
    return success_response(
        data=[WasteTrendPointResponse.model_validate(p) for p in points],
        message="Trend points retrieved",
    )
