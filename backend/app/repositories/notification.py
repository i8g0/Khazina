"""Notification Store data access."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.notification import Notification, NotificationReadReceipt
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository):
    """Persistence for notifications and read receipts."""

    def get_by_fingerprint(self, event_fingerprint: str) -> Notification | None:
        stmt = select(Notification).where(
            Notification.event_fingerprint == event_fingerprint
        )
        return self._session.scalars(stmt).first()

    def create(self, notification: Notification) -> Notification:
        return self._add(notification)

    def get(self, notification_id: uuid.UUID) -> Notification | None:
        return self._get(Notification, notification_id)

    def list_for_recipient(
        self,
        organization_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
        *,
        unread_only: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(
                Notification.organization_id == organization_id,
                Notification.recipient_user_id == recipient_user_id,
                Notification.status == "active",
            )
            .order_by(Notification.materialized_at.desc())
        )
        if unread_only:
            read_exists = (
                select(NotificationReadReceipt.id)
                .where(
                    NotificationReadReceipt.notification_id == Notification.id,
                    NotificationReadReceipt.user_id == recipient_user_id,
                )
                .exists()
            )
            stmt = stmt.where(~read_exists)
        stmt = self._paginate(stmt, limit, offset)
        return self._list(stmt)

    def count_unread(
        self,
        organization_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
    ) -> int:
        read_exists = (
            select(NotificationReadReceipt.id)
            .where(
                NotificationReadReceipt.notification_id == Notification.id,
                NotificationReadReceipt.user_id == recipient_user_id,
            )
            .exists()
        )
        stmt = select(func.count()).where(
            Notification.organization_id == organization_id,
            Notification.recipient_user_id == recipient_user_id,
            Notification.status == "active",
            ~read_exists,
        )
        return int(self._session.scalar(stmt) or 0)

    def unread_for_recipient(
        self,
        organization_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
    ) -> list[Notification]:
        return self.list_for_recipient(
            organization_id,
            recipient_user_id,
            unread_only=True,
        )

    def get_read_receipt(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> NotificationReadReceipt | None:
        stmt = select(NotificationReadReceipt).where(
            NotificationReadReceipt.notification_id == notification_id,
            NotificationReadReceipt.user_id == user_id,
        )
        return self._session.scalars(stmt).first()

    def create_read_receipt(
        self, receipt: NotificationReadReceipt
    ) -> NotificationReadReceipt:
        return self._add(receipt)

    def mark_all_read(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        *,
        read_at: datetime | None = None,
    ) -> int:
        unread = self.unread_for_recipient(organization_id, user_id)
        if not unread:
            return 0
        ts = read_at or datetime.now(timezone.utc)
        created = 0
        for notification in unread:
            if self.get_read_receipt(notification.id, user_id) is None:
                self.create_read_receipt(
                    NotificationReadReceipt(
                        notification_id=notification.id,
                        user_id=user_id,
                        read_at=ts,
                    )
                )
                created += 1
        return created
