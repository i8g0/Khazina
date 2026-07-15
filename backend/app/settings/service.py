"""Settings Service — deterministic org-scoped configuration authority."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.settings import OrganizationSettings
from app.repositories import OrganizationRepository, SettingsRepository
from app.services.base import BaseService
from app.services.exceptions import ResourceNotFoundError
from app.settings.exceptions import SettingsAccessError
from app.settings.models import PersistedSettingsDocument, ResolvedConfiguration
from app.settings.resolver import merge_patch, resolve_configuration, validate_patch_payload


class SettingsService(BaseService):
    """Reads, merges, validates, and persists organization settings."""

    def __init__(
        self,
        session: Session,
        settings_repository: SettingsRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        super().__init__(session)
        self._settings = settings_repository
        self._organizations = organization_repository

    def get_resolved_settings(
        self, organization_id: uuid.UUID
    ) -> ResolvedConfiguration:
        organization = self._require_active_organization(organization_id)
        persisted = self._load_or_initialize(organization_id)
        return resolve_configuration(organization, persisted)

    def get_document(
        self, organization_id: uuid.UUID
    ) -> PersistedSettingsDocument:
        self._require_active_organization(organization_id)
        record = self._settings.get_by_organization(organization_id)
        if record is None:
            return PersistedSettingsDocument()
        return PersistedSettingsDocument.from_dict(record.settings_document)

    def patch_settings(
        self,
        organization_id: uuid.UUID,
        patch: dict[str, Any],
    ) -> ResolvedConfiguration:
        organization = self._require_active_organization(organization_id)
        validate_patch_payload(patch)
        current = self._load_or_initialize(organization_id)
        merged = merge_patch(current, patch)
        resolved = resolve_configuration(organization, merged)
        payload = merged.to_dict()

        record = self._settings.get_by_organization(organization_id)
        with self._transaction():
            if record is None:
                record = OrganizationSettings(
                    organization_id=organization_id,
                    settings_document=payload,
                )
                self._settings.create(record)
            else:
                self._settings.update(record, {"settings_document": payload})
        return resolved

    def _load_or_initialize(
        self, organization_id: uuid.UUID
    ) -> PersistedSettingsDocument:
        record = self._settings.get_by_organization(organization_id)
        if record is None:
            with self._transaction():
                record = OrganizationSettings(
                    organization_id=organization_id,
                    settings_document={},
                )
                self._settings.create(record)
            return PersistedSettingsDocument()
        return PersistedSettingsDocument.from_dict(record.settings_document)

    def _require_active_organization(self, organization_id: uuid.UUID):
        organization = self._organizations.get_organization(organization_id)
        if organization is None:
            raise ResourceNotFoundError("Organization", organization_id)
        if not organization.is_active:
            raise SettingsAccessError(
                "Settings are not available for inactive organizations"
            )
        return organization
