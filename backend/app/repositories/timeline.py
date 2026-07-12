from __future__ import annotations

import uuid

from sqlalchemy import select

from app.db.models import TimelineEvent
from app.repositories.base import BaseRepository


class TimelineRepository(BaseRepository):
    """Data access for the Executive Timeline domain (append-only display events)."""

    def create(self, event: TimelineEvent) -> TimelineEvent:
        return self._add(event)

    def get(self, event_id: uuid.UUID) -> TimelineEvent | None:
        return self._get(TimelineEvent, event_id)

    def require(self, event_id: uuid.UUID) -> TimelineEvent:
        return self._require(TimelineEvent, event_id)

    def list_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        event_type: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[TimelineEvent]:
        """Dashboard timeline, newest events first (design §9)."""
        stmt = select(TimelineEvent).where(
            TimelineEvent.organization_id == organization_id
        )
        if event_type is not None:
            stmt = stmt.where(TimelineEvent.event_type == event_type)
        stmt = self._paginate(
            stmt.order_by(
                TimelineEvent.event_date.desc(), TimelineEvent.created_at.desc()
            ),
            limit,
            offset,
        )
        return self._list(stmt)

    def delete(self, event: TimelineEvent) -> None:
        self._delete(event)
