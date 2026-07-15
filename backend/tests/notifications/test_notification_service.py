"""NotificationService read-state and history tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.db.models.enums import RelatedEntityType
from app.db.models.notification import Notification, NotificationReadReceipt
from app.notifications.constants import KIND_ANALYSIS_COMPLETED
from app.notifications.service import NotificationService
from app.services.exceptions import OwnershipViolationError, ResourceNotFoundError


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def other_user_id() -> uuid.UUID:
    return uuid.uuid4()


def _notification(
    org_id: uuid.UUID,
    recipient_id: uuid.UUID,
    *,
    notification_id: uuid.UUID | None = None,
) -> Notification:
    return Notification(
        id=notification_id or uuid.uuid4(),
        organization_id=org_id,
        recipient_user_id=recipient_id,
        platform_event_kind=KIND_ANALYSIS_COMPLETED,
        title="Title",
        body="Body",
        source_entity_type=RelatedEntityType.ANALYSIS_RUN,
        source_entity_id=uuid.uuid4(),
        reporting_period_id=None,
        event_fingerprint="fp",
        payload_representation={},
        materialized_at=datetime.now(UTC),
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _service() -> tuple[NotificationService, MagicMock, MagicMock]:
    session = MagicMock()
    notification_repo = MagicMock()
    org_repo = MagicMock()
    org_repo.get_organization.return_value = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    return NotificationService(session, notification_repo, org_repo), notification_repo, org_repo


def test_new_notification_is_unread(org_id: uuid.UUID, user_id: uuid.UUID) -> None:
    service, repo, _ = _service()
    notification = _notification(org_id, user_id)
    repo.get.return_value = notification
    repo.get_read_receipt.return_value = None

    view = service.get_notification(org_id, user_id, notification.id)

    assert view.is_read is False
    assert view.read_at is None


def test_mark_read_creates_receipt(org_id: uuid.UUID, user_id: uuid.UUID) -> None:
    service, repo, _ = _service()
    notification = _notification(org_id, user_id)
    repo.get.return_value = notification
    receipt = NotificationReadReceipt(
        notification_id=notification.id,
        user_id=user_id,
        read_at=datetime.now(UTC),
    )
    repo.get_read_receipt.side_effect = [None, receipt]
    repo.create_read_receipt.side_effect = lambda r: r

    view = service.mark_read(org_id, user_id, notification.id)

    assert view.is_read is True
    repo.create_read_receipt.assert_called_once()


def test_mark_read_is_idempotent(org_id: uuid.UUID, user_id: uuid.UUID) -> None:
    service, repo, _ = _service()
    notification = _notification(org_id, user_id)
    receipt = NotificationReadReceipt(
        notification_id=notification.id,
        user_id=user_id,
        read_at=datetime.now(UTC),
    )
    repo.get.return_value = notification
    repo.get_read_receipt.return_value = receipt

    view = service.mark_read(org_id, user_id, notification.id)

    assert view.is_read is True
    repo.create_read_receipt.assert_not_called()


def test_mark_all_read_returns_count(org_id: uuid.UUID, user_id: uuid.UUID) -> None:
    service, repo, _ = _service()
    repo.mark_all_read.return_value = 3

    count = service.mark_all_read(org_id, user_id)

    assert count == 3
    repo.mark_all_read.assert_called_once_with(org_id, user_id)


def test_unread_count(org_id: uuid.UUID, user_id: uuid.UUID) -> None:
    service, repo, _ = _service()
    repo.count_unread.return_value = 2

    assert service.unread_count(org_id, user_id) == 2


def test_other_user_cannot_access_notification(
    org_id: uuid.UUID, user_id: uuid.UUID, other_user_id: uuid.UUID
) -> None:
    service, repo, _ = _service()
    notification = _notification(org_id, user_id)
    repo.get.return_value = notification

    with pytest.raises(OwnershipViolationError):
        service.get_notification(org_id, other_user_id, notification.id)


def test_missing_notification_raises_not_found(
    org_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    service, repo, _ = _service()
    repo.get.return_value = None
    missing_id = uuid.uuid4()

    with pytest.raises(ResourceNotFoundError):
        service.get_notification(org_id, user_id, missing_id)


def test_list_returns_only_recipient_views(org_id: uuid.UUID, user_id: uuid.UUID) -> None:
    service, repo, _ = _service()
    n1 = _notification(org_id, user_id)
    n2 = _notification(org_id, user_id)
    repo.list_for_recipient.return_value = [n1, n2]
    repo.get_read_receipt.return_value = None

    views = service.list_notifications(org_id, user_id)

    assert len(views) == 2
    assert all(not view.is_read for view in views)
    repo.list_for_recipient.assert_called_once()
