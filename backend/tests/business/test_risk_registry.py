"""Business engine registry includes risk engine."""

from __future__ import annotations

from app.business.bootstrap import initialize_business_engines
from app.business.registry import get_engine


def test_risk_engine_registered() -> None:
    initialize_business_engines()
    engine = get_engine("risk")
    assert engine.manifest.engine_id == "risk"
