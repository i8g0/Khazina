"""Settings resolver tests for report export preferences."""

from __future__ import annotations

import uuid

from app.db.models import Organization
from app.settings.models import PersistedSettingsDocument
from app.settings.resolver import resolve_configuration


def test_report_export_preferences_defaults() -> None:
    org = Organization(name="Org", platform_name="خزينة")
    org.id = uuid.uuid4()
    resolved = resolve_configuration(org, PersistedSettingsDocument())
    assert resolved.report_preferences.pdf_export_enabled is True
    assert resolved.report_preferences.pdf_include_cover_page is True
    assert resolved.report_preferences.pdf_include_provenance_appendix is True


def test_report_export_preferences_override() -> None:
    org = Organization(name="Org", platform_name="خزينة")
    org.id = uuid.uuid4()
    persisted = PersistedSettingsDocument(
        report_preferences={"pdf_export_enabled": False}
    )
    resolved = resolve_configuration(org, persisted)
    assert resolved.report_preferences.pdf_export_enabled is False
