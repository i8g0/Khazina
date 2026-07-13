"""User REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import PaginationDep, UserServiceDep
from app.api.permissions import require_org_role
from app.db.models.enums import UserRole
from app.schemas.response import ApiResponse, success_response
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(
    prefix="/organizations/{organization_id}/users",
    tags=["users"],
    dependencies=[Depends(require_org_role(UserRole.ADMIN))],
)


@router.post(
    "",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
)
def create_user(
    organization_id: UUID,
    body: UserCreate,
    service: UserServiceDep,
) -> ApiResponse[UserResponse]:
    user = service.create_user(
        organization_id,
        full_name=body.full_name,
        email=body.email,
        password=body.password,
        role=body.role,
    )
    return success_response(
        data=UserResponse.model_validate(user),
        message="User created",
    )


@router.get(
    "",
    response_model=ApiResponse[list[UserResponse]],
    summary="List users",
)
def list_users(
    organization_id: UUID,
    service: UserServiceDep,
    pagination: PaginationDep,
    active_only: bool = Query(False, description="Return only active users"),
) -> ApiResponse[list[UserResponse]]:
    users = service.list_users(
        organization_id,
        active_only=active_only,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[UserResponse.model_validate(u) for u in users],
        message="Users retrieved",
    )


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="Get user by ID",
)
def get_user(
    organization_id: UUID,
    user_id: UUID,
    service: UserServiceDep,
) -> ApiResponse[UserResponse]:
    user = service.get_user(organization_id, user_id)
    return success_response(
        data=UserResponse.model_validate(user),
        message="User retrieved",
    )


@router.patch(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="Update user",
)
def update_user(
    organization_id: UUID,
    user_id: UUID,
    body: UserUpdate,
    service: UserServiceDep,
) -> ApiResponse[UserResponse]:
    user = service.update_user(
        organization_id,
        user_id,
        full_name=body.full_name,
        email=body.email,
        password=body.password,
        role=body.role,
    )
    return success_response(
        data=UserResponse.model_validate(user),
        message="User updated",
    )


@router.post(
    "/{user_id}/deactivate",
    response_model=ApiResponse[UserResponse],
    summary="Deactivate user",
)
def deactivate_user(
    organization_id: UUID,
    user_id: UUID,
    service: UserServiceDep,
) -> ApiResponse[UserResponse]:
    user = service.deactivate_user(organization_id, user_id)
    return success_response(
        data=UserResponse.model_validate(user),
        message="User deactivated",
    )
