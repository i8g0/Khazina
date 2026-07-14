"""Scenario module isolation tests."""

from __future__ import annotations

from pathlib import Path


def test_scenario_module_does_not_import_ai() -> None:
    root = Path(__file__).resolve().parents[2] / "app" / "scenario"
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "app.ai" in text:
            offenders.append(str(path))
    assert offenders == []


def test_scenario_module_does_not_import_waste_engine() -> None:
    root = Path(__file__).resolve().parents[2] / "app" / "scenario"
    forbidden = ("app.business.engines.waste", 'get_engine("waste")', "WasteEngine(")
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                offenders.append(f"{path.name}:{token}")
    assert offenders == []
