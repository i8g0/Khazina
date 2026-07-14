"""Scenario Business Engine unit tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.business.engines.scenario.engine import ScenarioEngine
from app.business.engines.scenario.input import (
    ScenarioArchetype,
    ScenarioBaselineInput,
    ScenarioCategoryBaseline,
    ScenarioEngineInput,
)
from app.business.engines.scenario.manifest import SCENARIO_ENGINE_MANIFEST
from app.business.exceptions import ValidationError
from tests.scenario.conftest import sample_spending_reduction_input


def test_scenario_engine_returns_facts_contract() -> None:
    engine = ScenarioEngine()
    contract = engine.run(sample_spending_reduction_input())

    assert contract.engine_id == "scenario"
    assert contract.engine_version == "1.0.0"
    assert contract.contract_version == "1.0"
    baseline = next(f for f in contract.facts if f.metric == "scenario.baseline_total")
    projected = next(f for f in contract.facts if f.metric == "scenario.projected_total")
    assert float(baseline.value) == 48_750_000.0
    assert float(projected.value) == pytest.approx(43_875_000.0)


def test_scenario_engine_manifest() -> None:
    manifest = ScenarioEngine().manifest
    assert manifest.engine_id == SCENARIO_ENGINE_MANIFEST.engine_id
    assert manifest.supported_facts


def test_spending_reduction_requires_percent() -> None:
    engine = ScenarioEngine()
    baseline = ScenarioBaselineInput(
        total_baseline=100.0,
        categories=(ScenarioCategoryBaseline("a", 100.0),),
        generated_at=datetime(2026, 7, 15, tzinfo=UTC),
    )
    with pytest.raises(ValidationError):
        engine.run(
            ScenarioEngineInput(
                archetype=ScenarioArchetype.SPENDING_REDUCTION,
                baseline=baseline,
            )
        )
