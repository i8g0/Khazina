"""Department REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import DepartmentServiceDep, PaginationDep
from app.api.permissions import RequireOrgExecutive, require_org_role
from app.db.models.enums import UserRole
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.schemas.response import ApiResponse, success_response

router = APIRouter(
    prefix="/organizations/{organization_id}/departments",
    tags=["departments"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.post(
    "",
    response_model=ApiResponse[DepartmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create department",
)
def create_department(
    organization_id: UUID,
    body: DepartmentCreate,
    service: DepartmentServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[DepartmentResponse]:
    dept = service.create_department(
        organization_id,
        name_ar=body.name_ar,
        code=body.code,
        display_order=body.display_order,
    )
    return success_response(
        data=DepartmentResponse.model_validate(dept),
        message="Department created",
    )


@router.get(
    "",
    response_model=ApiResponse[list[DepartmentResponse]],
    summary="List departments",
)
def list_departments(
    organization_id: UUID,
    service: DepartmentServiceDep,
    pagination: PaginationDep,
    active_only: bool = Query(False, description="Return only active departments"),
) -> ApiResponse[list[DepartmentResponse]]:
    departments = service.list_departments(
        organization_id,
        active_only=active_only,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[DepartmentResponse.model_validate(d) for d in departments],
        message="Departments retrieved",
    )


@router.get(
    "/{department_id}",
    response_model=ApiResponse[DepartmentResponse],
    summary="Get department by ID",
)
def get_department(
    organization_id: UUID,
    department_id: UUID,
    service: DepartmentServiceDep,
) -> ApiResponse[DepartmentResponse]:
    dept = service.get_department(department_id)
    return success_response(
        data=DepartmentResponse.model_validate(dept),
        message="Department retrieved",
    )


@router.patch(
    "/{department_id}",
    response_model=ApiResponse[DepartmentResponse],
    summary="Update department",
)
def update_department(
    organization_id: UUID,
    department_id: UUID,
    body: DepartmentUpdate,
    service: DepartmentServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[DepartmentResponse]:
    dept = service.update_department(
        organization_id,
        department_id,
        name_ar=body.name_ar,
        code=body.code,
        display_order=body.display_order,
    )
    return success_response(
        data=DepartmentResponse.model_validate(dept),
        message="Department updated",
    )


@router.post(
    "/{department_id}/deactivate",
    response_model=ApiResponse[DepartmentResponse],
    summary="Deactivate department",
)
def deactivate_department(
    organization_id: UUID,
    department_id: UUID,
    service: DepartmentServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[DepartmentResponse]:
    dept = service.deactivate_department(organization_id, department_id)
    return success_response(
        data=DepartmentResponse.model_validate(dept),
        message="Department deactivated",
    )


@router.post(
    "/{department_id}/reactivate",
    response_model=ApiResponse[DepartmentResponse],
    summary="Reactivate department",
)
def reactivate_department(
    organization_id: UUID,
    department_id: UUID,
    service: DepartmentServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[DepartmentResponse]:
    dept = service.reactivate_department(organization_id, department_id)
    return success_response(
        data=DepartmentResponse.model_validate(dept),
        message="Department reactivated",
    )
