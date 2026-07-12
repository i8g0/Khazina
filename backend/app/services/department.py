"""Departmental Context service: governed department reference data."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.db.models import Department
from app.repositories import DepartmentRepository, OrganizationRepository
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    DuplicateResourceError,
    InvalidStateError,
    ResourceNotFoundError,
)


class DepartmentService(BaseService):
    """Business use cases for the governed department reference set.

    Departments are administered data (design §4.3): names are unique per
    organization and the approved lifecycle prefers deactivation over hard
    deletion so historical records keep their references.
    """

    def __init__(
        self,
        session: Session,
        department_repository: DepartmentRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        super().__init__(session)
        self._departments = department_repository
        self._organizations = organization_repository

    def create_department(
        self,
        organization_id: uuid.UUID,
        *,
        name_ar: str,
        code: str | None = None,
        display_order: int = 0,
    ) -> Department:
        self._require_organization(organization_id)
        name_ar = name_ar.strip()
        if not name_ar:
            raise BusinessValidationError("Department name must not be empty")
        if self._departments.get_by_name_ar(organization_id, name_ar) is not None:
            raise DuplicateResourceError(
                f"Department '{name_ar}' already exists for this organization"
            )

        department = Department(
            organization_id=organization_id,
            name_ar=name_ar,
            code=code,
            display_order=display_order,
        )
        with self._transaction():
            self._departments.create(department)
        return department

    def get_department(self, department_id: uuid.UUID) -> Department:
        return self._found(
            self._departments.get(department_id), "Department", department_id
        )

    def list_departments(
        self,
        organization_id: uuid.UUID,
        *,
        active_only: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Department]:
        self._require_organization(organization_id)
        return self._departments.list_for_organization(
            organization_id, active_only=active_only, limit=limit, offset=offset
        )

    def update_department(
        self,
        organization_id: uuid.UUID,
        department_id: uuid.UUID,
        *,
        name_ar: str | None = None,
        code: str | None = None,
        display_order: int | None = None,
    ) -> Department:
        department = self.get_department(department_id)
        self._check_ownership(department, "Department", organization_id)

        values: dict[str, object] = {}
        if name_ar is not None:
            name_ar = name_ar.strip()
            if not name_ar:
                raise BusinessValidationError("Department name must not be empty")
            if name_ar != department.name_ar:
                existing = self._departments.get_by_name_ar(organization_id, name_ar)
                if existing is not None and existing.id != department.id:
                    raise DuplicateResourceError(
                        f"Department '{name_ar}' already exists for this organization"
                    )
                values["name_ar"] = name_ar
        if code is not None:
            values["code"] = code
        if display_order is not None:
            values["display_order"] = display_order
        if not values:
            return department

        with self._transaction():
            self._departments.update(department, values)
        return department

    def deactivate_department(
        self, organization_id: uuid.UUID, department_id: uuid.UUID
    ) -> Department:
        """Approved lifecycle: deactivate instead of hard delete."""
        department = self.get_department(department_id)
        self._check_ownership(department, "Department", organization_id)
        if not department.is_active:
            raise InvalidStateError("Department is already inactive")
        with self._transaction():
            self._departments.update(department, {"is_active": False})
        return department

    def reactivate_department(
        self, organization_id: uuid.UUID, department_id: uuid.UUID
    ) -> Department:
        department = self.get_department(department_id)
        self._check_ownership(department, "Department", organization_id)
        if department.is_active:
            raise InvalidStateError("Department is already active")
        with self._transaction():
            self._departments.update(department, {"is_active": True})
        return department

    # -- internals -------------------------------------------------------------

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
