"""Current-user notification preference endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUserDep, UserNotificationPreferencesServiceDep
from app.api.permissions import require_org_role
from app.db.models.enums import UserRole
from app.schemas.response import ApiResponse, success_response
from app.schemas.user_notification_preferences import (
    UserNotificationPreferencesPatch,
    UserNotificationPreferencesResponse,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/users/me/notification-preferences",
    tags=["notification-preferences"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.get(
    "",
    response_model=ApiResponse[UserNotificationPreferencesResponse],
    summary="Get current user's notification preferences",
)
def get_user_notification_preferences(
    organization_id: UUID,
    service: UserNotificationPreferencesServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[UserNotificationPreferencesResponse]:
    resolved = service.get_preferences(organization_id, current_user.id)
    return success_response(
        data=UserNotificationPreferencesResponse(
            notifications_enabled=resolved.notifications_enabled,
            muted_notification_kinds=sorted(resolved.muted_notification_kinds),
            preferences_version=resolved.preferences_version,
        ),
        message="Notification preferences retrieved",
    )


@router.patch(
    "",
    response_model=ApiResponse[UserNotificationPreferencesResponse],
    summary="Patch current user's notification preferences",
)
def patch_user_notification_preferences(
    organization_id: UUID,
    body: UserNotificationPreferencesPatch,
    service: UserNotificationPreferencesServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[UserNotificationPreferencesResponse]:
    patch = body.model_dump(exclude_unset=True)
    resolved = service.patch_preferences(
        organization_id, current_user.id, patch
    )
    return success_response(
        data=UserNotificationPreferencesResponse(
            notifications_enabled=resolved.notifications_enabled,
            muted_notification_kinds=sorted(resolved.muted_notification_kinds),
            preferences_version=resolved.preferences_version,
        ),
        message="Notification preferences updated",
    )
