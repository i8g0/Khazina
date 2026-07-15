"""User notification REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserDep, NotificationServiceDep, PaginationDep
from app.api.permissions import require_org_role
from app.db.models.enums import UserRole
from app.notifications.service import NotificationView
from app.schemas.notification import (
    MarkAllReadResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.schemas.response import ApiResponse, success_response

router = APIRouter(
    prefix="/organizations/{organization_id}/notifications",
    tags=["notifications"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


def _to_response(view: NotificationView) -> NotificationResponse:
    notification = view.notification
    return NotificationResponse(
        id=notification.id,
        organization_id=notification.organization_id,
        recipient_user_id=notification.recipient_user_id,
        platform_event_kind=notification.platform_event_kind,
        title=notification.title,
        body=notification.body,
        source_entity_type=notification.source_entity_type,
        source_entity_id=notification.source_entity_id,
        reporting_period_id=notification.reporting_period_id,
        materialized_at=notification.materialized_at,
        status=notification.status,
        is_read=view.is_read,
        read_at=view.read_at,
        payload_representation=dict(notification.payload_representation or {}),
        created_at=notification.created_at,
        updated_at=notification.updated_at,
    )


@router.get(
    "",
    response_model=ApiResponse[list[NotificationResponse]],
    summary="List current user's notifications",
)
def list_notifications(
    organization_id: UUID,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
    pagination: PaginationDep,
    unread_only: bool = Query(False),
) -> ApiResponse[list[NotificationResponse]]:
    views = service.list_notifications(
        organization_id,
        current_user.id,
        unread_only=unread_only,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[_to_response(view) for view in views],
        message="Notifications retrieved",
    )


@router.get(
    "/unread-count",
    response_model=ApiResponse[UnreadCountResponse],
    summary="Unread notification count for current user",
)
def unread_notification_count(
    organization_id: UUID,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[UnreadCountResponse]:
    count = service.unread_count(organization_id, current_user.id)
    return success_response(
        data=UnreadCountResponse(unread_count=count),
        message="Unread count retrieved",
    )


@router.get(
    "/{notification_id}",
    response_model=ApiResponse[NotificationResponse],
    summary="Get notification by ID",
)
def get_notification(
    organization_id: UUID,
    notification_id: UUID,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[NotificationResponse]:
    view = service.get_notification(
        organization_id, current_user.id, notification_id
    )
    return success_response(
        data=_to_response(view),
        message="Notification retrieved",
    )


@router.post(
    "/{notification_id}/read",
    response_model=ApiResponse[NotificationResponse],
    summary="Mark notification as read",
)
def mark_notification_read(
    organization_id: UUID,
    notification_id: UUID,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[NotificationResponse]:
    view = service.mark_read(organization_id, current_user.id, notification_id)
    return success_response(
        data=_to_response(view),
        message="Notification marked as read",
    )


@router.post(
    "/read-all",
    response_model=ApiResponse[MarkAllReadResponse],
    summary="Mark all notifications as read for current user",
)
def mark_all_notifications_read(
    organization_id: UUID,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[MarkAllReadResponse]:
    marked = service.mark_all_read(organization_id, current_user.id)
    return success_response(
        data=MarkAllReadResponse(marked_count=marked),
        message="All notifications marked as read",
    )
