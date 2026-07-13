"""Ensure Business Engine layer has no AI dependencies."""

from __future__ import annotations

from pathlib import Path


def test_business_layer_does_not_import_ai() -> None:
    business_root = Path(__file__).resolve().parents[2] / "app" / "business"
    offenders: list[str] = []
    for path in business_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "app.ai" in text or "from app import ai" in text:
            offenders.append(str(path.relative_to(business_root.parent.parent)))
    assert offenders == []
