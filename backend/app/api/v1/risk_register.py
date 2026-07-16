"""Enterprise Risk Register governance REST endpoints (Sprint 9.4)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import PaginationDep, RiskRegisterServiceDep
from app.api.permissions import RequireOrgExecutive, require_org_role
from app.db.models.enums import UserRole
from app.schemas.response import ApiResponse, success_response
from app.schemas.risk import RiskResponse
from app.schemas.risk_analysis import RiskFindingResponse
from app.schemas.risk_register import (
    RiskEventResponse,
    RiskLifecycleStatusUpdate,
    RiskPromoteRequest,
    RiskPromotionResponse,
    RiskProvenanceResponse,
    RiskReviewRequest,
)

router = APIRouter(
    prefix="/organizations/{organization_id}",
    tags=["risk-register"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.post(
    "/risk-findings/{finding_id}/promote",
    response_model=ApiResponse[RiskPromotionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Promote a reviewed finding to the enterprise register",
)
def promote_finding(
    organization_id: UUID,
    finding_id: UUID,
    body: RiskPromoteRequest,
    service: RiskRegisterServiceDep,
    current_user: RequireOrgExecutive,
) -> ApiResponse[RiskPromotionResponse]:
    outcome = service.promote_finding(
        organization_id,
        finding_id,
        owner_label=body.owner_label,
        department_id=body.department_id,
        actor_user_id=current_user.id,
        reason=body.reason,
    )
    return success_response(
        data=RiskPromotionResponse(
            finding_id=outcome.finding.id,
            finding_status=outcome.finding.finding_status,
            risk=RiskResponse.model_validate(outcome.risk),
        ),
        message="Finding promoted to enterprise register",
    )


@router.post(
    "/risk-findings/{finding_id}/review",
    response_model=ApiResponse[RiskFindingResponse],
    summary="Review a risk finding",
)
def review_finding(
    organization_id: UUID,
    finding_id: UUID,
    body: RiskReviewRequest,
    service: RiskRegisterServiceDep,
    current_user: RequireOrgExecutive,
) -> ApiResponse[RiskFindingResponse]:
    finding = service.review_finding(
        organization_id,
        finding_id,
        body.action,
        reason=body.reason,
        actor_user_id=current_user.id,
    )
    return success_response(
        data=RiskFindingResponse.model_validate(finding),
        message="Finding review recorded",
    )


@router.patch(
    "/risks/{risk_id}/status",
    response_model=ApiResponse[RiskResponse],
    summary="Update enterprise risk lifecycle status",
)
def update_risk_lifecycle_status(
    organization_id: UUID,
    risk_id: UUID,
    body: RiskLifecycleStatusUpdate,
    service: RiskRegisterServiceDep,
    current_user: RequireOrgExecutive,
) -> ApiResponse[RiskResponse]:
    risk = service.update_lifecycle_status(
        organization_id,
        risk_id,
        body.lifecycle_status,
        reason=body.reason,
        actor_user_id=current_user.id,
    )
    return success_response(
        data=RiskResponse.model_validate(risk),
        message="Enterprise risk lifecycle updated",
    )


@router.post(
    "/risks/{risk_id}/review",
    response_model=ApiResponse[RiskResponse],
    summary="Apply a governance review action to an enterprise risk",
)
def review_risk(
    organization_id: UUID,
    risk_id: UUID,
    body: RiskReviewRequest,
    service: RiskRegisterServiceDep,
    current_user: RequireOrgExecutive,
) -> ApiResponse[RiskResponse]:
    risk = service.review_risk(
        organization_id,
        risk_id,
        body.action,
        reason=body.reason,
        actor_user_id=current_user.id,
    )
    return success_response(
        data=RiskResponse.model_validate(risk),
        message="Enterprise risk review recorded",
    )


@router.get(
    "/risks/{risk_id}/history",
    response_model=ApiResponse[list[RiskEventResponse]],
    summary="Get audit history for an enterprise risk",
)
def get_risk_history(
    organization_id: UUID,
    risk_id: UUID,
    service: RiskRegisterServiceDep,
    pagination: PaginationDep,
) -> ApiResponse[list[RiskEventResponse]]:
    events = service.get_risk_history(
        organization_id,
        risk_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[RiskEventResponse.model_validate(event) for event in events],
        message="Enterprise risk history retrieved",
    )


@router.get(
    "/risks/{risk_id}/provenance",
    response_model=ApiResponse[RiskProvenanceResponse],
    summary="Get full provenance chain for an enterprise risk",
)
def get_risk_provenance(
    organization_id: UUID,
    risk_id: UUID,
    service: RiskRegisterServiceDep,
) -> ApiResponse[RiskProvenanceResponse]:
    provenance = service.get_finding_provenance(organization_id, risk_id)
    return success_response(
        data=RiskProvenanceResponse.model_validate(provenance),
        message="Risk provenance retrieved",
    )
