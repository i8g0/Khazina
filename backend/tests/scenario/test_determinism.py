"""Scenario execution determinism tests."""

from __future__ import annotations

from app.business.bootstrap import initialize_business_engines
from app.business.engines.scenario.calculator import ScenarioCalculator
from app.business.registry import get_engine
from app.scenario.adapters.assumptions import ScenarioAssumptionsAdapter
from app.scenario.adapters.snapshot_v1 import ScenarioSnapshotAdapterV1
from tests.scenario.conftest import (
    sample_scenario_snapshot_payload,
    sample_spending_reduction_assumptions,
)


def test_same_inputs_produce_identical_facts_and_gold() -> None:
    initialize_business_engines()
    baseline = ScenarioSnapshotAdapterV1().adapt(
        sample_scenario_snapshot_payload(),
        organization_id="org-1",
        period="2026-Q2",
    )
    engine_input = ScenarioAssumptionsAdapter().adapt(
        sample_spending_reduction_assumptions(),
        scenario_name="تقليل الإنفاق 10%",
        scenario_description="محاكاة",
        baseline=baseline,
    )
    engine = get_engine("scenario")
    facts_a = engine.run(engine_input)
    facts_b = engine.run(engine_input)
    calc_a = ScenarioCalculator().calculate(engine_input)
    calc_b = ScenarioCalculator().calculate(engine_input)

    assert facts_a.to_dict() == facts_b.to_dict()
    assert calc_a.baseline_total == calc_b.baseline_total
    assert calc_a.projected_total == calc_b.projected_total
    assert calc_a.delta_percent == calc_b.delta_percent
