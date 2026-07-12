from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.db.models import Recommendation
from app.repositories.base import BaseRepository


class RecommendationRepository(BaseRepository):
    """Data access for the cross-cutting AI Recommendations domain."""

    def create(self, recommendation: Recommendation) -> Recommendation:
        return self._add(recommendation)

    def get(self, recommendation_id: uuid.UUID) -> Recommendation | None:
        return self._get(Recommendation, recommendation_id)

    def require(self, recommendation_id: uuid.UUID) -> Recommendation:
        return self._require(Recommendation, recommendation_id)

    def list_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        domain_source: str | None = None,
        priority: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Recommendation]:
        """Domain recommendation lists (design §9)."""
        stmt = select(Recommendation).where(
            Recommendation.organization_id == organization_id
        )
        if domain_source is not None:
            stmt = stmt.where(Recommendation.domain_source == domain_source)
        if priority is not None:
            stmt = stmt.where(Recommendation.priority == priority)
        stmt = self._paginate(
            stmt.order_by(Recommendation.created_at.desc()), limit, offset
        )
        return self._list(stmt)

    def list_dashboard_featured(
        self, organization_id: uuid.UUID, *, limit: int
    ) -> list[Recommendation]:
        """Dashboard top-N surfacing via the partial index on is_dashboard_featured."""
        stmt = (
            select(Recommendation)
            .where(
                Recommendation.organization_id == organization_id,
                Recommendation.is_dashboard_featured.is_(True),
            )
            .order_by(Recommendation.created_at.desc())
            .limit(limit)
        )
        return self._list(stmt)

    def list_for_analysis_run(self, analysis_run_id: uuid.UUID) -> list[Recommendation]:
        stmt = (
            select(Recommendation)
            .where(Recommendation.analysis_run_id == analysis_run_id)
            .order_by(Recommendation.created_at)
        )
        return self._list(stmt)

    def list_for_risk(self, risk_id: uuid.UUID) -> list[Recommendation]:
        stmt = (
            select(Recommendation)
            .where(Recommendation.risk_id == risk_id)
            .order_by(Recommendation.created_at)
        )
        return self._list(stmt)

    def list_for_simulation_run(
        self, simulation_run_id: uuid.UUID
    ) -> list[Recommendation]:
        stmt = (
            select(Recommendation)
            .where(Recommendation.simulation_run_id == simulation_run_id)
            .order_by(Recommendation.created_at)
        )
        return self._list(stmt)

    def update(
        self, recommendation: Recommendation, values: dict[str, Any]
    ) -> Recommendation:
        return self._update(recommendation, values)

    def delete(self, recommendation: Recommendation) -> None:
        self._delete(recommendation)
