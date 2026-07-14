"""AI Recommendation Service isolation tests."""

from __future__ import annotations

from pathlib import Path


def test_ai_recommendations_module_does_not_import_business_engines() -> None:
    root = Path(__file__).resolve().parents[2] / "app" / "ai_recommendations"
    offenders: list[str] = []
    forbidden = (
        "app.business.engines",
        "get_engine",
        "engine.run",
        "AiOrchestrator",
    )
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                offenders.append(f"{path.name}:{token}")
    assert offenders == []


def test_ai_recommendations_module_does_not_import_snapshot_layers() -> None:
    root = Path(__file__).resolve().parents[2] / "app" / "ai_recommendations"
    forbidden = (
        "FinancialSnapshot",
        "BronzeStorage",
        "app.ingestion",
        "app.decision",
    )
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                offenders.append(f"{path.name}:{token}")
    assert offenders == []
