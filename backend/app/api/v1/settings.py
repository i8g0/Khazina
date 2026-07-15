"""Organization settings REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import SettingsServiceDep
from app.api.permissions import RequireOrgAdmin, require_org_role
from app.db.models.enums import UserRole
from app.schemas.response import ApiResponse, success_response
from app.schemas.settings import ResolvedSettingsResponse, SettingsPatchRequest
from app.settings.models import ResolvedConfiguration


router = APIRouter(
    prefix="/organizations/{organization_id}/settings",
    tags=["settings"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


def _to_response(resolved: ResolvedConfiguration) -> ResolvedSettingsResponse:
    return ResolvedSettingsResponse.model_validate(resolved.to_api_dict())


@router.get(
    "",
    response_model=ApiResponse[ResolvedSettingsResponse],
    summary="Get resolved organization settings",
)
def get_organization_settings(
    organization_id: UUID,
    service: SettingsServiceDep,
) -> ApiResponse[ResolvedSettingsResponse]:
    resolved = service.get_resolved_settings(organization_id)
    return success_response(
        data=_to_response(resolved),
        message="Organization settings retrieved",
    )


@router.patch(
    "",
    response_model=ApiResponse[ResolvedSettingsResponse],
    summary="Patch organization settings",
)
def patch_organization_settings(
    organization_id: UUID,
    body: SettingsPatchRequest,
    service: SettingsServiceDep,
    _current_user: RequireOrgAdmin,
) -> ApiResponse[ResolvedSettingsResponse]:
    resolved = service.patch_settings(organization_id, body.to_patch_dict())
    return success_response(
        data=_to_response(resolved),
        message="Organization settings updated",
    )
