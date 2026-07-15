"""Notification history and read-state service."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.notification import Notification, NotificationReadReceipt
from app.repositories import NotificationRepository, OrganizationRepository
from app.services.base import BaseService
from app.services.exceptions import OwnershipViolationError, ResourceNotFoundError


@dataclass(frozen=True, slots=True)
class NotificationView:
    notification: Notification
    is_read: bool
    read_at: datetime | None


class NotificationService(BaseService):
    """User notification history — list, read state, mark read."""

    def __init__(
        self,
        session: Session,
        notification_repository: NotificationRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        super().__init__(session)
        self._notifications = notification_repository
        self._organizations = organization_repository

    def list_notifications(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        *,
        unread_only: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[NotificationView]:
        self._require_organization(organization_id)
        rows = self._notifications.list_for_recipient(
            organization_id,
            user_id,
            unread_only=unread_only,
            limit=limit,
            offset=offset,
        )
        return [self._to_view(row, user_id) for row in rows]

    def get_notification(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> NotificationView:
        self._require_organization(organization_id)
        notification = self._owned_notification(organization_id, user_id, notification_id)
        return self._to_view(notification, user_id)

    def unread_count(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> int:
        self._require_organization(organization_id)
        return self._notifications.count_unread(organization_id, user_id)

    def mark_read(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> NotificationView:
        notification = self._owned_notification(organization_id, user_id, notification_id)
        existing = self._notifications.get_read_receipt(notification.id, user_id)
        if existing is None:
            with self._transaction():
                self._notifications.create_read_receipt(
                    NotificationReadReceipt(
                        notification_id=notification.id,
                        user_id=user_id,
                        read_at=datetime.now(timezone.utc),
                    )
                )
        return self._to_view(notification, user_id)

    def mark_all_read(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> int:
        self._require_organization(organization_id)
        with self._transaction():
            return self._notifications.mark_all_read(organization_id, user_id)

    def _owned_notification(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> Notification:
        notification = self._notifications.get(notification_id)
        if notification is None:
            raise ResourceNotFoundError("Notification", notification_id)
        if notification.organization_id != organization_id:
            raise ResourceNotFoundError("Notification", notification_id)
        if notification.recipient_user_id != user_id:
            raise OwnershipViolationError(
                f"Notification '{notification_id}' is not addressed to user '{user_id}'"
            )
        return notification

    def _to_view(self, notification: Notification, user_id: uuid.UUID) -> NotificationView:
        receipt = self._notifications.get_read_receipt(notification.id, user_id)
        return NotificationView(
            notification=notification,
            is_read=receipt is not None,
            read_at=receipt.read_at if receipt else None,
        )

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
