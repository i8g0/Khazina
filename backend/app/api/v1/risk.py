"""Risk management REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import PaginationDep, RiskServiceDep
from app.schemas.response import ApiResponse, success_response
from app.schemas.risk import (
    MitigationPlanCreate,
    MitigationPlanResponse,
    MitigationPlanUpdate,
    RiskCreate,
    RiskResponse,
    RiskTransitionRequest,
    RiskUpdate,
)

router = APIRouter(
    prefix="/organizations/{organization_id}",
    tags=["risk"],
)


@router.post(
    "/risks",
    response_model=ApiResponse[RiskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register risk",
)
def register_risk(
    organization_id: UUID,
    body: RiskCreate,
    service: RiskServiceDep,
) -> ApiResponse[RiskResponse]:
    risk = service.register_risk(
        organization_id,
        name=body.name,
        description=body.description,
        priority=body.priority,
        score=body.score,
        department_id=body.department_id,
        reporting_period_id=body.reporting_period_id,
        owner_label=body.owner_label,
        likelihood=body.likelihood,
        impact=body.impact,
        category_label=body.category_label,
    )
    return success_response(
        data=RiskResponse.model_validate(risk),
        message="Risk registered",
    )


@router.get(
    "/risks",
    response_model=ApiResponse[list[RiskResponse]],
    summary="List risks",
)
def list_risks(
    organization_id: UUID,
    service: RiskServiceDep,
    pagination: PaginationDep,
    status_filter: str | None = Query(None, alias="status"),
    priority: str | None = Query(None),
    department_id: UUID | None = Query(None),
) -> ApiResponse[list[RiskResponse]]:
    risks = service.list_risks(
        organization_id,
        status=status_filter,
        priority=priority,
        department_id=department_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[RiskResponse.model_validate(r) for r in risks],
        message="Risks retrieved",
    )


@router.get(
    "/risks/{risk_id}",
    response_model=ApiResponse[RiskResponse],
    summary="Get risk by ID",
)
def get_risk(
    organization_id: UUID,
    risk_id: UUID,
    service: RiskServiceDep,
) -> ApiResponse[RiskResponse]:
    risk = service.get_risk(risk_id)
    return success_response(
        data=RiskResponse.model_validate(risk),
        message="Risk retrieved",
    )


@router.patch(
    "/risks/{risk_id}",
    response_model=ApiResponse[RiskResponse],
    summary="Update risk",
)
def update_risk(
    organization_id: UUID,
    risk_id: UUID,
    body: RiskUpdate,
    service: RiskServiceDep,
) -> ApiResponse[RiskResponse]:
    risk = service.update_risk(
        organization_id,
        risk_id,
        name=body.name,
        description=body.description,
        priority=body.priority,
        score=body.score,
        owner_label=body.owner_label,
        likelihood=body.likelihood,
        impact=body.impact,
        category_label=body.category_label,
    )
    return success_response(
        data=RiskResponse.model_validate(risk),
        message="Risk updated",
    )


@router.post(
    "/risks/{risk_id}/transition",
    response_model=ApiResponse[RiskResponse],
    summary="Transition risk status",
)
def transition_risk(
    organization_id: UUID,
    risk_id: UUID,
    body: RiskTransitionRequest,
    service: RiskServiceDep,
) -> ApiResponse[RiskResponse]:
    risk = service.transition_risk(organization_id, risk_id, body.status)
    return success_response(
        data=RiskResponse.model_validate(risk),
        message="Risk status updated",
    )


@router.delete(
    "/risks/{risk_id}",
    response_model=ApiResponse[None],
    summary="Delete risk",
)
def delete_risk(
    organization_id: UUID,
    risk_id: UUID,
    service: RiskServiceDep,
) -> ApiResponse[None]:
    service.delete_risk(organization_id, risk_id)
    return success_response(data=None, message="Risk deleted")


# -- Mitigation plans ----------------------------------------------------------


@router.post(
    "/risks/{risk_id}/mitigation-plans",
    response_model=ApiResponse[MitigationPlanResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add mitigation plan",
)
def add_mitigation_plan(
    organization_id: UUID,
    risk_id: UUID,
    body: MitigationPlanCreate,
    service: RiskServiceDep,
) -> ApiResponse[MitigationPlanResponse]:
    plan = service.add_mitigation_plan(
        organization_id,
        risk_id,
        title=body.title,
        description=body.description,
        status=body.status,
        target_date=body.target_date,
        owner_label=body.owner_label,
    )
    return success_response(
        data=MitigationPlanResponse.model_validate(plan),
        message="Mitigation plan added",
    )


@router.get(
    "/risks/{risk_id}/mitigation-plans",
    response_model=ApiResponse[list[MitigationPlanResponse]],
    summary="List mitigation plans for a risk",
)
def list_mitigation_plans(
    organization_id: UUID,
    risk_id: UUID,
    service: RiskServiceDep,
) -> ApiResponse[list[MitigationPlanResponse]]:
    plans = service.list_mitigation_plans(organization_id, risk_id)
    return success_response(
        data=[MitigationPlanResponse.model_validate(p) for p in plans],
        message="Mitigation plans retrieved",
    )


@router.get(
    "/mitigation-plans",
    response_model=ApiResponse[list[MitigationPlanResponse]],
    summary="List mitigation plans across organization",
)
def list_organization_mitigation_plans(
    organization_id: UUID,
    service: RiskServiceDep,
    pagination: PaginationDep,
) -> ApiResponse[list[MitigationPlanResponse]]:
    plans = service.list_mitigation_plans_for_organization(
        organization_id, limit=pagination.limit, offset=pagination.offset
    )
    return success_response(
        data=[MitigationPlanResponse.model_validate(p) for p in plans],
        message="Mitigation plans retrieved",
    )


@router.patch(
    "/mitigation-plans/{plan_id}",
    response_model=ApiResponse[MitigationPlanResponse],
    summary="Update mitigation plan",
)
def update_mitigation_plan(
    organization_id: UUID,
    plan_id: UUID,
    body: MitigationPlanUpdate,
    service: RiskServiceDep,
) -> ApiResponse[MitigationPlanResponse]:
    plan = service.update_mitigation_plan(
        organization_id,
        plan_id,
        title=body.title,
        description=body.description,
        status=body.status,
        target_date=body.target_date,
        owner_label=body.owner_label,
    )
    return success_response(
        data=MitigationPlanResponse.model_validate(plan),
        message="Mitigation plan updated",
    )


@router.delete(
    "/mitigation-plans/{plan_id}",
    response_model=ApiResponse[None],
    summary="Delete mitigation plan",
)
def delete_mitigation_plan(
    organization_id: UUID,
    plan_id: UUID,
    service: RiskServiceDep,
) -> ApiResponse[None]:
    service.delete_mitigation_plan(organization_id, plan_id)
    return success_response(data=None, message="Mitigation plan deleted")
