from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.db.models.settings import OrganizationSettings
from app.repositories.base import BaseRepository


class SettingsRepository(BaseRepository):
    """Data access for organization-scoped settings documents."""

    def get_by_organization(
        self, organization_id: uuid.UUID
    ) -> OrganizationSettings | None:
        stmt = select(OrganizationSettings).where(
            OrganizationSettings.organization_id == organization_id
        )
        return self._session.scalars(stmt).first()

    def create(self, record: OrganizationSettings) -> OrganizationSettings:
        return self._add(record)

    def update(
        self, record: OrganizationSettings, values: dict[str, Any]
    ) -> OrganizationSettings:
        return self._update(record, values)
