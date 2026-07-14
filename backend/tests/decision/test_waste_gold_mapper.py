"""Unit tests for Waste Gold mapper."""

from __future__ import annotations

import pytest

from app.business.engines.waste import WasteEngine
from app.decision.adapters.waste_v1 import WasteSnapshotAdapterV1
from app.decision.mappers.waste_gold import WasteGoldMapper
from tests.decision.conftest import sample_waste_payload


def test_gold_mapper_matches_engine_output(business_engines_initialized: None) -> None:
    adapter = WasteSnapshotAdapterV1()
    engine_input = adapter.adapt(sample_waste_payload())
    engine = WasteEngine()
    facts = engine.run(engine_input)
    payload = WasteGoldMapper.to_record_payload(facts)

    assert payload["total_waste_amount"] == 2_340_000.0
    assert payload["waste_percentage"] == pytest.approx(4.68)
    assert payload["top_category_name"] == "finance"
    assert len(payload["category_breakdowns"]) == 3
    assert payload["category_breakdowns"][0]["category_name"] == "finance"
