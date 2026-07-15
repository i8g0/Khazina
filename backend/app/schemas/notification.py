"""Notification API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.common import FullTimestampResponse, SchemaBase


class NotificationResponse(FullTimestampResponse):
    id: UUID
    organization_id: UUID
    recipient_user_id: UUID
    platform_event_kind: str
    title: str
    body: str
    source_entity_type: str
    source_entity_id: UUID
    reporting_period_id: UUID | None
    materialized_at: datetime
    status: str
    is_read: bool
    read_at: datetime | None = None
    payload_representation: dict[str, Any] = Field(default_factory=dict)


class UnreadCountResponse(SchemaBase):
    unread_count: int


class MarkAllReadResponse(SchemaBase):
    marked_count: int
