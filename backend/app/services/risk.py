"""Enterprise Risk Management services: risk lifecycle and mitigation plans."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.db.models import Risk, RiskMitigationPlan
from app.db.models.enums import RiskPriority, RiskStatus
from app.repositories import (
    DepartmentRepository,
    OrganizationRepository,
    RiskRepository,
)
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    InvalidStateError,
    InvalidStateTransitionError,
    ResourceNotFoundError,
)

# Approved risk lifecycle (design §4.7): active → in_progress → closed.
# Closing is terminal; work may also close directly from active.
_RISK_TRANSITIONS: dict[str, set[str]] = {
    RiskStatus.ACTIVE: {RiskStatus.IN_PROGRESS, RiskStatus.CLOSED},
    RiskStatus.IN_PROGRESS: {RiskStatus.CLOSED},
    RiskStatus.CLOSED: set(),
}


class RiskService(BaseService):
    """Business use cases for the risk register and mitigation planning."""

    def __init__(
        self,
        session: Session,
        risk_repository: RiskRepository,
        organization_repository: OrganizationRepository,
        department_repository: DepartmentRepository,
    ) -> None:
        super().__init__(session)
        self._risks = risk_repository
        self._organizations = organization_repository
        self._departments = department_repository

    # -- risk register -----------------------------------------------------------

    def register_risk(
        self,
        organization_id: uuid.UUID,
        *,
        name: str,
        description: str,
        priority: str,
        score: int,
        department_id: uuid.UUID | None = None,
        reporting_period_id: uuid.UUID | None = None,
        owner_label: str | None = None,
        likelihood: str | None = None,
        impact: str | None = None,
        category_label: str | None = None,
    ) -> Risk:
        self._require_organization(organization_id)
        name = name.strip()
        description = description.strip()
        if not name or not description:
            raise BusinessValidationError(
                "Risk name and description must not be empty"
            )
        self._validate_priority(priority)
        self._validate_score(score)
        if department_id is not None:
            self._require_owned_department(organization_id, department_id)
        if reporting_period_id is not None:
            self._require_owned_period(organization_id, reporting_period_id)

        risk = Risk(
            organization_id=organization_id,
            department_id=department_id,
            reporting_period_id=reporting_period_id,
            name=name,
            description=description,
            priority=priority,
            score=score,
            status=RiskStatus.ACTIVE,
            owner_label=owner_label,
            likelihood=likelihood,
            impact=impact,
            category_label=category_label,
            last_updated_at=date.today(),
        )
        with self._transaction():
            self._risks.create(risk)
        return risk

    def get_risk(self, risk_id: uuid.UUID) -> Risk:
        return self._found(self._risks.get(risk_id), "Risk", risk_id)

    def list_risks(
        self,
        organization_id: uuid.UUID,
        *,
        status: str | None = None,
        priority: str | None = None,
        department_id: uuid.UUID | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Risk]:
        self._require_organization(organization_id)
        return self._risks.list_for_organization(
            organization_id,
            status=status,
            priority=priority,
            department_id=department_id,
            limit=limit,
            offset=offset,
        )

    def update_risk(
        self,
        organization_id: uuid.UUID,
        risk_id: uuid.UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        score: int | None = None,
        owner_label: str | None = None,
        likelihood: str | None = None,
        impact: str | None = None,
        category_label: str | None = None,
    ) -> Risk:
        risk = self._owned_risk(organization_id, risk_id)
        if risk.status == RiskStatus.CLOSED:
            raise InvalidStateError("A closed risk cannot be modified")

        values: dict[str, object] = {}
        if name is not None:
            name = name.strip()
            if not name:
                raise BusinessValidationError("Risk name must not be empty")
            values["name"] = name
        if description is not None:
            description = description.strip()
            if not description:
                raise BusinessValidationError("Risk description must not be empty")
            values["description"] = description
        if priority is not None:
            self._validate_priority(priority)
            values["priority"] = priority
        if score is not None:
            self._validate_score(score)
            values["score"] = score
        if owner_label is not None:
            values["owner_label"] = owner_label
        if likelihood is not None:
            values["likelihood"] = likelihood
        if impact is not None:
            values["impact"] = impact
        if category_label is not None:
            values["category_label"] = category_label
        if not values:
            return risk
        values["last_updated_at"] = date.today()

        with self._transaction():
            self._risks.update(risk, values)
        return risk

    def transition_risk(
        self, organization_id: uuid.UUID, risk_id: uuid.UUID, new_status: str
    ) -> Risk:
        risk = self._owned_risk(organization_id, risk_id)
        if new_status not in set(RiskStatus):
            raise BusinessValidationError(f"Unknown risk status '{new_status}'")
        allowed = _RISK_TRANSITIONS.get(risk.status, set())
        if new_status not in allowed:
            raise InvalidStateTransitionError("Risk", risk.status, new_status)
        with self._transaction():
            self._risks.update(
                risk, {"status": new_status, "last_updated_at": date.today()}
            )
        return risk

    def delete_risk(self, organization_id: uuid.UUID, risk_id: uuid.UUID) -> None:
        """Deletes a risk and its cascading mitigation plans."""
        risk = self._owned_risk(organization_id, risk_id)
        with self._transaction():
            self._risks.delete(risk)

    # -- mitigation plans -----------------------------------------------------------

    def add_mitigation_plan(
        self,
        organization_id: uuid.UUID,
        risk_id: uuid.UUID,
        *,
        title: str,
        description: str,
        status: str,
        target_date: date,
        owner_label: str | None = None,
    ) -> RiskMitigationPlan:
        risk = self._owned_risk(organization_id, risk_id)
        if risk.status == RiskStatus.CLOSED:
            raise InvalidStateError(
                "Mitigation plans cannot be added to a closed risk"
            )
        title = title.strip()
        description = description.strip()
        status = status.strip()
        if not title or not description or not status:
            raise BusinessValidationError(
                "Mitigation plan title, description, and status must not be empty"
            )

        plan = RiskMitigationPlan(
            risk_id=risk.id,
            title=title,
            description=description,
            status=status,
            target_date=target_date,
            owner_label=owner_label,
        )
        with self._transaction():
            self._risks.add_mitigation_plan(plan)
            self._risks.update(risk, {"last_updated_at": date.today()})
        return plan

    def list_mitigation_plans(
        self, organization_id: uuid.UUID, risk_id: uuid.UUID
    ) -> list[RiskMitigationPlan]:
        self._owned_risk(organization_id, risk_id)
        return self._risks.list_mitigation_plans(risk_id)

    def list_mitigation_plans_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[RiskMitigationPlan]:
        self._require_organization(organization_id)
        return self._risks.list_mitigation_plans_for_organization(
            organization_id, limit=limit, offset=offset
        )

    def update_mitigation_plan(
        self,
        organization_id: uuid.UUID,
        plan_id: uuid.UUID,
        *,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        target_date: date | None = None,
        owner_label: str | None = None,
    ) -> RiskMitigationPlan:
        plan = self._found(
            self._risks.get_mitigation_plan(plan_id), "RiskMitigationPlan", plan_id
        )
        self._owned_risk(organization_id, plan.risk_id)

        values: dict[str, object] = {}
        if title is not None:
            title = title.strip()
            if not title:
                raise BusinessValidationError("Plan title must not be empty")
            values["title"] = title
        if description is not None:
            description = description.strip()
            if not description:
                raise BusinessValidationError("Plan description must not be empty")
            values["description"] = description
        if status is not None:
            status = status.strip()
            if not status:
                raise BusinessValidationError("Plan status must not be empty")
            values["status"] = status
        if target_date is not None:
            values["target_date"] = target_date
        if owner_label is not None:
            values["owner_label"] = owner_label
        if not values:
            return plan

        with self._transaction():
            self._risks.update_mitigation_plan(plan, values)
        return plan

    def delete_mitigation_plan(
        self, organization_id: uuid.UUID, plan_id: uuid.UUID
    ) -> None:
        plan = self._found(
            self._risks.get_mitigation_plan(plan_id), "RiskMitigationPlan", plan_id
        )
        self._owned_risk(organization_id, plan.risk_id)
        with self._transaction():
            self._risks.delete_mitigation_plan(plan)

    # -- internals ---------------------------------------------------------------------

    def _owned_risk(self, organization_id: uuid.UUID, risk_id: uuid.UUID) -> Risk:
        risk = self.get_risk(risk_id)
        self._check_ownership(risk, "Risk", organization_id)
        return risk

    @staticmethod
    def _validate_priority(priority: str) -> None:
        if priority not in set(RiskPriority):
            raise BusinessValidationError(f"Unknown risk priority '{priority}'")

    @staticmethod
    def _validate_score(score: int) -> None:
        if not 0 <= score <= 100:
            raise BusinessValidationError("Risk score must be between 0 and 100")

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)

    def _require_owned_department(
        self, organization_id: uuid.UUID, department_id: uuid.UUID
    ) -> None:
        department = self._departments.get(department_id)
        if department is None:
            raise ResourceNotFoundError("Department", department_id)
        self._check_ownership(department, "Department", organization_id)

    def _require_owned_period(
        self, organization_id: uuid.UUID, period_id: uuid.UUID
    ) -> None:
        period = self._organizations.get_reporting_period(period_id)
        if period is None:
            raise ResourceNotFoundError("ReportingPeriod", period_id)
        self._check_ownership(period, "ReportingPeriod", organization_id)
