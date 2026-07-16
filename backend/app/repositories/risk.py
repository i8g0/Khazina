from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.db.models import Risk, RiskMitigationPlan
from app.repositories.base import BaseRepository


class RiskRepository(BaseRepository):
    """Data access for the Enterprise Risk Management domain (risks, mitigation plans)."""

    # -- risks ---------------------------------------------------------------

    def create(self, risk: Risk) -> Risk:
        return self._add(risk)

    def get(self, risk_id: uuid.UUID) -> Risk | None:
        return self._get(Risk, risk_id)

    def require(self, risk_id: uuid.UUID) -> Risk:
        return self._require(Risk, risk_id)

    def list_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        status: str | None = None,
        priority: str | None = None,
        department_id: uuid.UUID | None = None,
        lifecycle_status: str | None = None,
        category_code: str | None = None,
        source_type: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Risk]:
        """Risk register filtering by status/priority/department (design §9)."""
        stmt = select(Risk).where(Risk.organization_id == organization_id)
        if status is not None:
            stmt = stmt.where(Risk.status == status)
        if lifecycle_status is not None:
            stmt = stmt.where(Risk.lifecycle_status == lifecycle_status)
        if priority is not None:
            stmt = stmt.where(Risk.priority == priority)
        if department_id is not None:
            stmt = stmt.where(Risk.department_id == department_id)
        if category_code is not None:
            stmt = stmt.where(Risk.category_code == category_code)
        if source_type is not None:
            stmt = stmt.where(Risk.source_type == source_type)
        stmt = self._paginate(
            stmt.order_by(Risk.last_updated_at.desc(), Risk.score.desc()),
            limit,
            offset,
        )
        return self._list(stmt)

    def get_by_source_finding_id(
        self, source_finding_id: uuid.UUID
    ) -> Risk | None:
        stmt = select(Risk).where(Risk.source_finding_id == source_finding_id)
        return self._session.scalars(stmt).first()

    def count_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        status: str | None = None,
        priority: str | None = None,
    ) -> int:
        stmt = select(Risk).where(Risk.organization_id == organization_id)
        if status is not None:
            stmt = stmt.where(Risk.status == status)
        if priority is not None:
            stmt = stmt.where(Risk.priority == priority)
        return self._count(stmt)

    def update(self, risk: Risk, values: dict[str, Any]) -> Risk:
        return self._update(risk, values)

    def delete(self, risk: Risk) -> None:
        """Deletes the risk; mitigation plans cascade at DB level."""
        self._delete(risk)

    # -- mitigation plans -----------------------------------------------------

    def add_mitigation_plan(self, plan: RiskMitigationPlan) -> RiskMitigationPlan:
        return self._add(plan)

    def get_mitigation_plan(self, plan_id: uuid.UUID) -> RiskMitigationPlan | None:
        return self._get(RiskMitigationPlan, plan_id)

    def list_mitigation_plans(self, risk_id: uuid.UUID) -> list[RiskMitigationPlan]:
        stmt = (
            select(RiskMitigationPlan)
            .where(RiskMitigationPlan.risk_id == risk_id)
            .order_by(RiskMitigationPlan.target_date)
        )
        return self._list(stmt)

    def list_mitigation_plans_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[RiskMitigationPlan]:
        """Mitigation plans timeline across all risks (Risk page section)."""
        stmt = self._paginate(
            select(RiskMitigationPlan)
            .join(Risk, RiskMitigationPlan.risk_id == Risk.id)
            .where(Risk.organization_id == organization_id)
            .order_by(RiskMitigationPlan.target_date),
            limit,
            offset,
        )
        return self._list(stmt)

    def update_mitigation_plan(
        self, plan: RiskMitigationPlan, values: dict[str, Any]
    ) -> RiskMitigationPlan:
        return self._update(plan, values)

    def delete_mitigation_plan(self, plan: RiskMitigationPlan) -> None:
        self._delete(plan)
