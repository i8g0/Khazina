"""Report module isolation tests."""

from __future__ import annotations

from pathlib import Path


def test_reports_module_does_not_import_ai() -> None:
    root = Path(__file__).resolve().parents[2] / "app" / "reports"
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "app.ai" in text:
            offenders.append(str(path))
    assert offenders == []


def test_reports_module_does_not_import_business_engines() -> None:
    root = Path(__file__).resolve().parents[2] / "app" / "reports"
    forbidden = (
        "get_engine(",
        "engine.run(",
    )
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "app.business.engines" in text and path.name != "sections.py":
            offenders.append(str(path))
        for token in forbidden:
            if token in text:
                offenders.append(f"{path.name}:{token}")
    assert offenders == []
