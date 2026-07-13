"""Recommendation REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import PaginationDep, RecommendationServiceDep
from app.api.permissions import RequireOrgAdmin, RequireOrgExecutive, require_org_role
from app.db.models.enums import UserRole
from app.schemas.recommendation import RecommendationCreate, RecommendationResponse
from app.schemas.response import ApiResponse, success_response

router = APIRouter(
    prefix="/organizations/{organization_id}/recommendations",
    tags=["recommendations"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.post(
    "",
    response_model=ApiResponse[RecommendationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register recommendation",
)
def register_recommendation(
    organization_id: UUID,
    body: RecommendationCreate,
    service: RecommendationServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[RecommendationResponse]:
    recommendation = service.register_recommendation(
        organization_id,
        domain_source=body.domain_source,
        title=body.title,
        description=body.description,
        priority=body.priority,
        external_ref=body.external_ref,
        confidence_label=body.confidence_label,
        estimated_savings_amount=body.estimated_savings_amount,
        department_id=body.department_id,
        analysis_run_id=body.analysis_run_id,
        risk_id=body.risk_id,
        simulation_run_id=body.simulation_run_id,
        is_dashboard_featured=body.is_dashboard_featured,
        source_context=body.source_context,
    )
    return success_response(
        data=RecommendationResponse.model_validate(recommendation),
        message="Recommendation registered",
    )


@router.get(
    "",
    response_model=ApiResponse[list[RecommendationResponse]],
    summary="List recommendations",
)
def list_recommendations(
    organization_id: UUID,
    service: RecommendationServiceDep,
    pagination: PaginationDep,
    domain_source: str | None = Query(None),
    priority: str | None = Query(None),
) -> ApiResponse[list[RecommendationResponse]]:
    recommendations = service.list_recommendations(
        organization_id,
        domain_source=domain_source,
        priority=priority,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[RecommendationResponse.model_validate(r) for r in recommendations],
        message="Recommendations retrieved",
    )


@router.get(
    "/dashboard-featured",
    response_model=ApiResponse[list[RecommendationResponse]],
    summary="List dashboard-featured recommendations",
)
def list_dashboard_featured(
    organization_id: UUID,
    service: RecommendationServiceDep,
    limit: int = Query(5, ge=1, le=50),
) -> ApiResponse[list[RecommendationResponse]]:
    recommendations = service.list_dashboard_featured(
        organization_id, limit=limit
    )
    return success_response(
        data=[RecommendationResponse.model_validate(r) for r in recommendations],
        message="Dashboard recommendations retrieved",
    )


@router.get(
    "/{recommendation_id}",
    response_model=ApiResponse[RecommendationResponse],
    summary="Get recommendation by ID",
)
def get_recommendation(
    organization_id: UUID,
    recommendation_id: UUID,
    service: RecommendationServiceDep,
) -> ApiResponse[RecommendationResponse]:
    recommendation = service.get_recommendation(recommendation_id)
    return success_response(
        data=RecommendationResponse.model_validate(recommendation),
        message="Recommendation retrieved",
    )


@router.post(
    "/{recommendation_id}/feature",
    response_model=ApiResponse[RecommendationResponse],
    summary="Feature recommendation on dashboard",
)
def feature_on_dashboard(
    organization_id: UUID,
    recommendation_id: UUID,
    service: RecommendationServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[RecommendationResponse]:
    recommendation = service.feature_on_dashboard(
        organization_id, recommendation_id
    )
    return success_response(
        data=RecommendationResponse.model_validate(recommendation),
        message="Recommendation featured on dashboard",
    )


@router.post(
    "/{recommendation_id}/unfeature",
    response_model=ApiResponse[RecommendationResponse],
    summary="Remove recommendation from dashboard",
)
def unfeature_from_dashboard(
    organization_id: UUID,
    recommendation_id: UUID,
    service: RecommendationServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[RecommendationResponse]:
    recommendation = service.unfeature_from_dashboard(
        organization_id, recommendation_id
    )
    return success_response(
        data=RecommendationResponse.model_validate(recommendation),
        message="Recommendation removed from dashboard",
    )


@router.delete(
    "/{recommendation_id}",
    response_model=ApiResponse[None],
    summary="Delete recommendation",
)
def delete_recommendation(
    organization_id: UUID,
    recommendation_id: UUID,
    service: RecommendationServiceDep,
    _current_user: RequireOrgAdmin,
) -> ApiResponse[None]:
    service.delete_recommendation(organization_id, recommendation_id)
    return success_response(data=None, message="Recommendation deleted")
