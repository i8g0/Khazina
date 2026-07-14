"""Determinism tests for Decision Engine path."""

from __future__ import annotations

from datetime import UTC, datetime

from app.business.engines.waste import WasteEngine
from app.business.registry import get_engine
from app.business.engines.waste.manifest import ENGINE_ID
from app.decision.adapters.waste_v1 import WasteSnapshotAdapterV1
from tests.decision.conftest import sample_waste_payload


def test_same_snapshot_produces_identical_facts_json(
    business_engines_initialized: None,
) -> None:
    adapter = WasteSnapshotAdapterV1()
    payload = sample_waste_payload()
    fixed_time = datetime(2026, 7, 15, tzinfo=UTC)
    first_input = adapter.adapt(
        payload, organization_id="org-1", period="2026-Q2", generated_at=fixed_time
    )
    second_input = adapter.adapt(
        payload, organization_id="org-1", period="2026-Q2", generated_at=fixed_time
    )

    engine = get_engine(ENGINE_ID)
    first_facts = engine.run(first_input)
    second_facts = engine.run(second_input)

    assert first_facts.to_json() == second_facts.to_json()


def test_adapter_determinism_same_bytes(business_engines_initialized: None) -> None:
    adapter = WasteSnapshotAdapterV1()
    payload = sample_waste_payload()
    fixed_time = datetime(2026, 7, 15, tzinfo=UTC)
    first = adapter.adapt(payload, generated_at=fixed_time)
    second = adapter.adapt(payload, generated_at=fixed_time)

    assert first.total_spend == second.total_spend
    assert first.total_waste_amount == second.total_waste_amount
    assert first.categories == second.categories

    engine = WasteEngine()
    assert engine.run(first).to_json() == engine.run(second).to_json()
