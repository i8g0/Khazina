from __future__ import annotations

import uuid

from sqlalchemy import select

from app.db.models import RiskEvent
from app.repositories.base import BaseRepository


class RiskEventRepository(BaseRepository):
    """Append-only audit trail for enterprise risk governance."""

    def append(self, event: RiskEvent) -> RiskEvent:
        return self._add(event)

    def list_for_risk(
        self,
        risk_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[RiskEvent]:
        stmt = (
            select(RiskEvent)
            .where(RiskEvent.risk_id == risk_id)
            .order_by(RiskEvent.created_at.desc())
        )
        stmt = self._paginate(stmt, limit, offset)
        return self._list(stmt)

    def list_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        event_type: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[RiskEvent]:
        stmt = select(RiskEvent).where(
            RiskEvent.organization_id == organization_id
        )
        if event_type is not None:
            stmt = stmt.where(RiskEvent.event_type == event_type)
        stmt = stmt.order_by(RiskEvent.created_at.desc())
        stmt = self._paginate(stmt, limit, offset)
        return self._list(stmt)
