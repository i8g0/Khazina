"""Settings resolver determinism tests."""

from __future__ import annotations

import uuid

import pytest

from app.db.models import Organization
from app.settings.exceptions import SettingsValidationError
from app.settings.models import PersistedSettingsDocument
from app.settings.resolver import merge_patch, resolve_configuration, validate_patch_payload


@pytest.fixture
def organization() -> Organization:
    org = Organization(name="Acme Corp", platform_name="خزينة")
    org.id = uuid.uuid4()
    org.is_active = True
    return org


def test_resolve_configuration_platform_defaults(organization: Organization) -> None:
    resolved = resolve_configuration(organization, PersistedSettingsDocument())
    assert resolved.organization_identity.name == "Acme Corp"
    assert resolved.organization_settings.locale == "ar"
    assert resolved.ai_configuration.ai_recommendations_enabled is True
    assert resolved.localization.prompt_language_source == "deployment"
    assert "financial_waste" in resolved.analysis_configuration.enabled_analysis_types


def test_resolve_configuration_localization_override(organization: Organization) -> None:
    persisted = PersistedSettingsDocument(
        localization={"prompt_language": "en", "report_language": "en"}
    )
    resolved = resolve_configuration(organization, persisted)
    assert resolved.localization.prompt_language == "en"
    assert resolved.localization.report_language == "en"
    assert resolved.localization.prompt_language_source == "organization"


def test_resolve_configuration_report_language_fallback_to_prompt(
    organization: Organization,
) -> None:
    persisted = PersistedSettingsDocument(localization={"prompt_language": "en"})
    resolved = resolve_configuration(organization, persisted)
    assert resolved.localization.report_language == "en"
    assert resolved.localization.report_language_source == "prompt_language"


def test_merge_patch_rejects_forbidden_keys() -> None:
    with pytest.raises(SettingsValidationError, match="Forbidden"):
        validate_patch_payload({"ai_configuration": {"ollama_model": "hack"}})


def test_merge_patch_null_clears_localization_override(organization: Organization) -> None:
    persisted = PersistedSettingsDocument(localization={"prompt_language": "en"})
    merged = merge_patch(
        persisted,
        {"localization": {"prompt_language": None}},
    )
    resolved = resolve_configuration(organization, merged)
    assert resolved.localization.prompt_language_source == "deployment"


def test_identical_inputs_produce_identical_resolution(
    organization: Organization,
) -> None:
    persisted = PersistedSettingsDocument(
        ai_configuration={"ai_recommendations_enabled": False}
    )
    first = resolve_configuration(organization, persisted)
    second = resolve_configuration(organization, persisted)
    assert first.to_api_dict() == second.to_api_dict()
