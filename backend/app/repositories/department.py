from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.db.models import Department
from app.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository):
    """Data access for the Departmental Context domain (governed department reference data)."""

    def create(self, department: Department) -> Department:
        return self._add(department)

    def get(self, department_id: uuid.UUID) -> Department | None:
        return self._get(Department, department_id)

    def require(self, department_id: uuid.UUID) -> Department:
        return self._require(Department, department_id)

    def get_by_name_ar(
        self, organization_id: uuid.UUID, name_ar: str
    ) -> Department | None:
        stmt = select(Department).where(
            Department.organization_id == organization_id,
            Department.name_ar == name_ar,
        )
        return self._session.scalars(stmt).first()

    def list_for_organization(
        self,
        organization_id: uuid.UUID,
        *,
        active_only: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Department]:
        stmt = select(Department).where(Department.organization_id == organization_id)
        if active_only:
            stmt = stmt.where(Department.is_active.is_(True))
        stmt = self._paginate(
            stmt.order_by(Department.display_order, Department.name_ar), limit, offset
        )
        return self._list(stmt)

    def update(self, department: Department, values: dict[str, Any]) -> Department:
        return self._update(department, values)

    def delete(self, department: Department) -> None:
        """Hard delete; approved lifecycle prefers deactivation via is_active."""
        self._delete(department)
