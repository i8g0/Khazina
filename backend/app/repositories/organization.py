from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.db.models import Organization, ReportingPeriod
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository):
    """Data access for the Organization Context domain (organizations, reporting periods)."""

    # -- organizations ----------------------------------------------------

    def create_organization(self, organization: Organization) -> Organization:
        return self._add(organization)

    def get_organization(self, organization_id: uuid.UUID) -> Organization | None:
        return self._get(Organization, organization_id)

    def require_organization(self, organization_id: uuid.UUID) -> Organization:
        return self._require(Organization, organization_id)

    def get_active_organization(self) -> Organization | None:
        """Single active organization expected in MVP (design §4.1)."""
        stmt = (
            select(Organization)
            .where(Organization.is_active.is_(True))
            .order_by(Organization.created_at)
            .limit(1)
        )
        return self._session.scalars(stmt).first()

    def list_organizations(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> list[Organization]:
        stmt = self._paginate(
            select(Organization).order_by(Organization.created_at), limit, offset
        )
        return self._list(stmt)

    def update_organization(
        self, organization: Organization, values: dict[str, Any]
    ) -> Organization:
        return self._update(organization, values)

    # -- reporting periods -------------------------------------------------

    def create_reporting_period(self, period: ReportingPeriod) -> ReportingPeriod:
        return self._add(period)

    def get_reporting_period(self, period_id: uuid.UUID) -> ReportingPeriod | None:
        return self._get(ReportingPeriod, period_id)

    def require_reporting_period(self, period_id: uuid.UUID) -> ReportingPeriod:
        return self._require(ReportingPeriod, period_id)

    def get_active_reporting_period(
        self, organization_id: uuid.UUID
    ) -> ReportingPeriod | None:
        """At most one active period per organization (partial unique index)."""
        stmt = select(ReportingPeriod).where(
            ReportingPeriod.organization_id == organization_id,
            ReportingPeriod.is_active.is_(True),
        )
        return self._session.scalars(stmt).first()

    def list_reporting_periods(
        self,
        organization_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ReportingPeriod]:
        stmt = self._paginate(
            select(ReportingPeriod)
            .where(ReportingPeriod.organization_id == organization_id)
            .order_by(ReportingPeriod.created_at.desc()),
            limit,
            offset,
        )
        return self._list(stmt)

    def update_reporting_period(
        self, period: ReportingPeriod, values: dict[str, Any]
    ) -> ReportingPeriod:
        return self._update(period, values)

    def delete_reporting_period(self, period: ReportingPeriod) -> None:
        self._delete(period)
