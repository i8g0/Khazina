"""Organization Context services: organization lifecycle and reporting periods."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.db.models import Organization, ReportingPeriod
from app.repositories import OrganizationRepository
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    DuplicateResourceError,
    InvalidStateError,
)


class OrganizationService(BaseService):
    """Business use cases for organizations and their reporting periods.

    MVP rule (design §4.1): the platform operates on a single active
    organization; creating a second active organization is rejected.
    Reporting periods follow the "at most one active period per
    organization" rule enforced here and by the partial unique index.
    """

    def __init__(
        self,
        session: Session,
        organization_repository: OrganizationRepository,
    ) -> None:
        super().__init__(session)
        self._organizations = organization_repository

    # -- organization lifecycle ---------------------------------------------

    def create_organization(
        self,
        *,
        name: str,
        platform_name: str | None = None,
        executive_title: str | None = None,
    ) -> Organization:
        name = name.strip()
        if not name:
            raise BusinessValidationError("Organization name must not be empty")
        if self._organizations.get_active_organization() is not None:
            raise DuplicateResourceError(
                "An active organization already exists; "
                "the MVP operates on a single organization context"
            )

        organization = Organization(name=name, executive_title=executive_title)
        if platform_name is not None:
            organization.platform_name = platform_name

        with self._transaction():
            self._organizations.create_organization(organization)
        return organization

    def get_organization(self, organization_id: uuid.UUID) -> Organization:
        return self._found(
            self._organizations.get_organization(organization_id),
            "Organization",
            organization_id,
        )

    def get_active_organization(self) -> Organization:
        organization = self._organizations.get_active_organization()
        if organization is None:
            raise InvalidStateError("No active organization is configured")
        return organization

    def update_organization(
        self,
        organization_id: uuid.UUID,
        *,
        name: str | None = None,
        platform_name: str | None = None,
        executive_title: str | None = None,
    ) -> Organization:
        organization = self.get_organization(organization_id)

        values: dict[str, object] = {}
        if name is not None:
            name = name.strip()
            if not name:
                raise BusinessValidationError("Organization name must not be empty")
            values["name"] = name
        if platform_name is not None:
            values["platform_name"] = platform_name
        if executive_title is not None:
            values["executive_title"] = executive_title
        if not values:
            return organization

        with self._transaction():
            self._organizations.update_organization(organization, values)
        return organization

    def deactivate_organization(self, organization_id: uuid.UUID) -> Organization:
        organization = self.get_organization(organization_id)
        if not organization.is_active:
            raise InvalidStateError("Organization is already inactive")
        with self._transaction():
            self._organizations.update_organization(
                organization, {"is_active": False}
            )
        return organization

    # -- reporting periods ---------------------------------------------------

    def create_reporting_period(
        self,
        organization_id: uuid.UUID,
        *,
        label: str,
        start_date: date | None = None,
        end_date: date | None = None,
        activate: bool = False,
    ) -> ReportingPeriod:
        organization = self.get_organization(organization_id)
        label = label.strip()
        if not label:
            raise BusinessValidationError("Reporting period label must not be empty")
        self._validate_date_range(start_date, end_date)

        period = ReportingPeriod(
            organization_id=organization.id,
            label=label,
            start_date=start_date,
            end_date=end_date,
            is_active=activate,
        )

        with self._transaction():
            if activate:
                self._deactivate_current_period(organization.id)
            self._organizations.create_reporting_period(period)
        return period

    def get_reporting_period(self, period_id: uuid.UUID) -> ReportingPeriod:
        return self._found(
            self._organizations.get_reporting_period(period_id),
            "ReportingPeriod",
            period_id,
        )

    def list_reporting_periods(
        self,
        organization_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ReportingPeriod]:
        self.get_organization(organization_id)
        return self._organizations.list_reporting_periods(
            organization_id, limit=limit, offset=offset
        )

    def activate_reporting_period(
        self, organization_id: uuid.UUID, period_id: uuid.UUID
    ) -> ReportingPeriod:
        """Switch the active period; the previous active period is closed first."""
        period = self.get_reporting_period(period_id)
        self._check_ownership(period, "ReportingPeriod", organization_id)
        if period.is_active:
            raise InvalidStateError("Reporting period is already active")

        with self._transaction():
            self._deactivate_current_period(organization_id)
            self._organizations.update_reporting_period(period, {"is_active": True})
        return period

    def close_active_reporting_period(
        self, organization_id: uuid.UUID
    ) -> ReportingPeriod:
        period = self._organizations.get_active_reporting_period(organization_id)
        if period is None:
            raise InvalidStateError(
                "Organization has no active reporting period to close"
            )
        with self._transaction():
            self._organizations.update_reporting_period(period, {"is_active": False})
        return period

    def update_reporting_period(
        self,
        organization_id: uuid.UUID,
        period_id: uuid.UUID,
        *,
        label: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> ReportingPeriod:
        period = self.get_reporting_period(period_id)
        self._check_ownership(period, "ReportingPeriod", organization_id)

        values: dict[str, object] = {}
        if label is not None:
            label = label.strip()
            if not label:
                raise BusinessValidationError(
                    "Reporting period label must not be empty"
                )
            values["label"] = label
        new_start = start_date if start_date is not None else period.start_date
        new_end = end_date if end_date is not None else period.end_date
        self._validate_date_range(new_start, new_end)
        if start_date is not None:
            values["start_date"] = start_date
        if end_date is not None:
            values["end_date"] = end_date
        if not values:
            return period

        with self._transaction():
            self._organizations.update_reporting_period(period, values)
        return period

    def delete_reporting_period(
        self, organization_id: uuid.UUID, period_id: uuid.UUID
    ) -> None:
        period = self.get_reporting_period(period_id)
        self._check_ownership(period, "ReportingPeriod", organization_id)
        if period.is_active:
            raise InvalidStateError(
                "Active reporting period cannot be deleted; close it first"
            )
        with self._transaction():
            self._organizations.delete_reporting_period(period)

    # -- internals -------------------------------------------------------------

    def _deactivate_current_period(self, organization_id: uuid.UUID) -> None:
        current = self._organizations.get_active_reporting_period(organization_id)
        if current is not None:
            self._organizations.update_reporting_period(current, {"is_active": False})

    @staticmethod
    def _validate_date_range(start_date: date | None, end_date: date | None) -> None:
        if start_date is not None and end_date is not None and end_date < start_date:
            raise BusinessValidationError(
                "Reporting period end date must not precede its start date"
            )
