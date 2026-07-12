"""Executive timeline API schemas."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampResponse


class TimelineEventCreate(SchemaBase):
    title: str = Field(..., min_length=1, max_length=500)
    event_type: str = Field(..., max_length=50)
    event_date: date | None = None
    reporting_period_id: UUID | None = None
    related_entity_type: str | None = Field(None, max_length=50)
    related_entity_id: UUID | None = None


class TimelineEventResponse(TimestampResponse):
    id: UUID
    organization_id: UUID
    reporting_period_id: UUID | None
    event_date: date
    title: str
    event_type: str
    related_entity_type: str | None
    related_entity_id: UUID | None
