"""SettingsService orchestration tests."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.db.models import Organization
from app.db.models.settings import OrganizationSettings
from app.settings.exceptions import SettingsAccessError, SettingsValidationError
from app.settings.service import SettingsService


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def active_org(org_id: uuid.UUID) -> Organization:
    org = Organization(name="Org", platform_name="خزينة")
    org.id = org_id
    org.is_active = True
    return org


def _service(
    org_id: uuid.UUID,
    *,
    active_org: Organization | None = None,
    settings_record: OrganizationSettings | None = None,
) -> SettingsService:
    session = MagicMock()
    settings_repo = MagicMock()
    org_repo = MagicMock()
    org = active_org or Organization(name="Org", platform_name="خزينة")
    org.id = org_id
    if active_org is None:
        org.is_active = True
    org_repo.get_organization.return_value = org
    settings_repo.get_by_organization.return_value = settings_record
    settings_repo.create.side_effect = lambda record: record
    settings_repo.update.side_effect = lambda record, values: setattr(
        record, "settings_document", values["settings_document"]
    ) or record
    session.commit = MagicMock()
    session.rollback = MagicMock()
    return SettingsService(session, settings_repo, org_repo)


def test_get_resolved_settings_lazy_init(org_id: uuid.UUID) -> None:
    service = _service(org_id)
    resolved = service.get_resolved_settings(org_id)
    assert resolved.ai_configuration.ai_recommendations_enabled is True
    assert service._settings.create.called  # type: ignore[attr-defined]


def test_inactive_organization_fails_closed(org_id: uuid.UUID) -> None:
    inactive = MagicMock(spec=Organization)
    inactive.id = org_id
    inactive.is_active = False
    service = _service(org_id, active_org=inactive)
    with pytest.raises(SettingsAccessError):
        service.get_resolved_settings(org_id)


def test_patch_settings_persists_valid_changes(org_id: uuid.UUID) -> None:
    record = OrganizationSettings(organization_id=org_id, settings_document={})
    service = _service(org_id, settings_record=record)
    resolved = service.patch_settings(
        org_id,
        {"ai_configuration": {"ai_recommendations_enabled": False}},
    )
    assert resolved.ai_configuration.ai_recommendations_enabled is False


def test_patch_settings_rejects_forbidden_keys(org_id: uuid.UUID) -> None:
    record = OrganizationSettings(organization_id=org_id, settings_document={})
    service = _service(org_id, settings_record=record)
    with pytest.raises(SettingsValidationError):
        service.patch_settings(org_id, {"localization": {"ollama_url": "http://x"}})
