"""Organization and reporting period REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import OrganizationServiceDep, PaginationDep
from app.api.permissions import (
    RequireAdmin,
    RequireAnalyst,
    RequireOrgAdmin,
    RequireOrgAnalyst,
    RequireOrgExecutive,
)
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    ReportingPeriodCreate,
    ReportingPeriodResponse,
    ReportingPeriodUpdate,
)
from app.schemas.response import ApiResponse, success_response

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "",
    response_model=ApiResponse[OrganizationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
)
def create_organization(
    body: OrganizationCreate,
    service: OrganizationServiceDep,
    _current_user: RequireAdmin,
) -> ApiResponse[OrganizationResponse]:
    org = service.create_organization(
        name=body.name,
        platform_name=body.platform_name,
        executive_title=body.executive_title,
    )
    return success_response(
        data=OrganizationResponse.model_validate(org),
        message="Organization created",
    )


@router.get(
    "/active",
    response_model=ApiResponse[OrganizationResponse],
    summary="Get active organization",
)
def get_active_organization(
    service: OrganizationServiceDep,
    _current_user: RequireAnalyst,
) -> ApiResponse[OrganizationResponse]:
    org = service.get_active_organization()
    return success_response(
        data=OrganizationResponse.model_validate(org),
        message="Active organization retrieved",
    )


@router.get(
    "/{organization_id}",
    response_model=ApiResponse[OrganizationResponse],
    summary="Get organization by ID",
)
def get_organization(
    organization_id: UUID,
    service: OrganizationServiceDep,
    _current_user: RequireOrgAnalyst,
) -> ApiResponse[OrganizationResponse]:
    org = service.get_organization(organization_id)
    return success_response(
        data=OrganizationResponse.model_validate(org),
        message="Organization retrieved",
    )


@router.patch(
    "/{organization_id}",
    response_model=ApiResponse[OrganizationResponse],
    summary="Update organization",
)
def update_organization(
    organization_id: UUID,
    body: OrganizationUpdate,
    service: OrganizationServiceDep,
    _current_user: RequireOrgAdmin,
) -> ApiResponse[OrganizationResponse]:
    org = service.update_organization(
        organization_id,
        name=body.name,
        platform_name=body.platform_name,
        executive_title=body.executive_title,
    )
    return success_response(
        data=OrganizationResponse.model_validate(org),
        message="Organization updated",
    )


@router.post(
    "/{organization_id}/deactivate",
    response_model=ApiResponse[OrganizationResponse],
    summary="Deactivate organization",
)
def deactivate_organization(
    organization_id: UUID,
    service: OrganizationServiceDep,
    _current_user: RequireOrgAdmin,
) -> ApiResponse[OrganizationResponse]:
    org = service.deactivate_organization(organization_id)
    return success_response(
        data=OrganizationResponse.model_validate(org),
        message="Organization deactivated",
    )


# -- Reporting periods ---------------------------------------------------------


@router.post(
    "/{organization_id}/reporting-periods",
    response_model=ApiResponse[ReportingPeriodResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create reporting period",
)
def create_reporting_period(
    organization_id: UUID,
    body: ReportingPeriodCreate,
    service: OrganizationServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[ReportingPeriodResponse]:
    period = service.create_reporting_period(
        organization_id,
        label=body.label,
        start_date=body.start_date,
        end_date=body.end_date,
        activate=body.activate,
    )
    return success_response(
        data=ReportingPeriodResponse.model_validate(period),
        message="Reporting period created",
    )


@router.get(
    "/{organization_id}/reporting-periods",
    response_model=ApiResponse[list[ReportingPeriodResponse]],
    summary="List reporting periods",
)
def list_reporting_periods(
    organization_id: UUID,
    service: OrganizationServiceDep,
    pagination: PaginationDep,
    _current_user: RequireOrgAnalyst,
) -> ApiResponse[list[ReportingPeriodResponse]]:
    periods = service.list_reporting_periods(
        organization_id, limit=pagination.limit, offset=pagination.offset
    )
    return success_response(
        data=[ReportingPeriodResponse.model_validate(p) for p in periods],
        message="Reporting periods retrieved",
    )


@router.get(
    "/{organization_id}/reporting-periods/{period_id}",
    response_model=ApiResponse[ReportingPeriodResponse],
    summary="Get reporting period by ID",
)
def get_reporting_period(
    organization_id: UUID,
    period_id: UUID,
    service: OrganizationServiceDep,
    _current_user: RequireOrgAnalyst,
) -> ApiResponse[ReportingPeriodResponse]:
    period = service.get_reporting_period(period_id)
    return success_response(
        data=ReportingPeriodResponse.model_validate(period),
        message="Reporting period retrieved",
    )


@router.patch(
    "/{organization_id}/reporting-periods/{period_id}",
    response_model=ApiResponse[ReportingPeriodResponse],
    summary="Update reporting period",
)
def update_reporting_period(
    organization_id: UUID,
    period_id: UUID,
    body: ReportingPeriodUpdate,
    service: OrganizationServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[ReportingPeriodResponse]:
    period = service.update_reporting_period(
        organization_id,
        period_id,
        label=body.label,
        start_date=body.start_date,
        end_date=body.end_date,
    )
    return success_response(
        data=ReportingPeriodResponse.model_validate(period),
        message="Reporting period updated",
    )


@router.post(
    "/{organization_id}/reporting-periods/{period_id}/activate",
    response_model=ApiResponse[ReportingPeriodResponse],
    summary="Activate reporting period",
)
def activate_reporting_period(
    organization_id: UUID,
    period_id: UUID,
    service: OrganizationServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[ReportingPeriodResponse]:
    period = service.activate_reporting_period(organization_id, period_id)
    return success_response(
        data=ReportingPeriodResponse.model_validate(period),
        message="Reporting period activated",
    )


@router.post(
    "/{organization_id}/reporting-periods/close-active",
    response_model=ApiResponse[ReportingPeriodResponse],
    summary="Close active reporting period",
)
def close_active_reporting_period(
    organization_id: UUID,
    service: OrganizationServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[ReportingPeriodResponse]:
    period = service.close_active_reporting_period(organization_id)
    return success_response(
        data=ReportingPeriodResponse.model_validate(period),
        message="Active reporting period closed",
    )


@router.delete(
    "/{organization_id}/reporting-periods/{period_id}",
    response_model=ApiResponse[None],
    summary="Delete reporting period",
)
def delete_reporting_period(
    organization_id: UUID,
    period_id: UUID,
    service: OrganizationServiceDep,
    _current_user: RequireOrgAdmin,
) -> ApiResponse[None]:
    service.delete_reporting_period(organization_id, period_id)
    return success_response(data=None, message="Reporting period deleted")
