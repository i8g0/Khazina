"""Sprint 6.9 isolation tests."""

from __future__ import annotations

from pathlib import Path


def test_reports_export_modules_do_not_import_ai() -> None:
    root = Path(__file__).resolve().parents[2] / "app" / "reports"
    offenders: list[str] = []
    for name in ("export_service.py", "pdf_renderer.py", "export_storage.py"):
        text = (root / name).read_text(encoding="utf-8")
        if "app.ai" in text:
            offenders.append(name)
    assert offenders == []


def test_notifications_preference_modules_do_not_import_ai() -> None:
    root = Path(__file__).resolve().parents[2] / "app" / "notifications"
    offenders: list[str] = []
    for name in (
        "effective_preferences.py",
        "user_preferences_service.py",
        "user_preferences_resolver.py",
    ):
        text = (root / name).read_text(encoding="utf-8")
        if "app.ai" in text:
            offenders.append(name)
    assert offenders == []


def test_no_dashboard_or_repository_summary_routes() -> None:
    router = (
        Path(__file__).resolve().parents[2] / "app" / "api" / "v1" / "router.py"
    ).read_text(encoding="utf-8")
    assert "dashboard" not in router.lower()
    assert "repository_summary" not in router.lower()
