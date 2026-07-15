"""ScenarioAssumptionsAdapter tests."""

from __future__ import annotations

import uuid

import pytest

from app.business.engines.scenario.input import ScenarioArchetype
from app.db.models.simulation import SimulationAssumption
from app.decision.exceptions import SnapshotAdapterError
from app.scenario.adapters.assumptions import ScenarioAssumptionsAdapter
from tests.scenario.conftest import (
    sample_baseline_input,
    sample_spending_reduction_assumptions,
)


def test_adapt_spending_reduction() -> None:
    result = ScenarioAssumptionsAdapter().adapt(
        sample_spending_reduction_assumptions(),
        scenario_name="تقليل الإنفاق 10%",
        scenario_description="محاكاة خفض الإنفاق",
        baseline=sample_baseline_input(),
    )
    assert result.archetype == ScenarioArchetype.SPENDING_REDUCTION
    assert result.reduction_percent == 10.0
    assert result.horizon_quarters == 3


def test_index_assumptions_accepts_dict_input() -> None:
    index = ScenarioAssumptionsAdapter._index_assumptions(
        sample_spending_reduction_assumptions()
    )
    assert index.by_normalized_label["نسبة خفض الإنفاق"] == "10%"
    assert index.by_normalized_label["الأفق الزمني"] == "3 أرباع"


def test_index_assumptions_accepts_simulation_assumption_objects() -> None:
    assumptions = [
        SimulationAssumption(
            scenario_id=uuid.uuid4(),
            label="نسبة خفض الإنفاق",
            value="10%",
        ),
        SimulationAssumption(
            scenario_id=uuid.uuid4(),
            label="الأفق الزمني",
            value="3 أرباع",
        ),
    ]
    index = ScenarioAssumptionsAdapter._index_assumptions(assumptions)
    assert index.by_normalized_label["نسبة خفض الإنفاق"] == "10%"
    assert index.by_normalized_label["الأفق الزمني"] == "3 أرباع"


def test_adapt_spending_reduction_with_simulation_assumption_objects() -> None:
    assumptions = [
        SimulationAssumption(
            scenario_id=uuid.uuid4(),
            label="نسبة خفض الإنفاق",
            value="10%",
        ),
        SimulationAssumption(
            scenario_id=uuid.uuid4(),
            label="نطاق التطبيق",
            value="جميع الأقسام",
        ),
        SimulationAssumption(
            scenario_id=uuid.uuid4(),
            label="الأفق الزمني",
            value="3 أرباع",
        ),
    ]
    result = ScenarioAssumptionsAdapter().adapt(
        assumptions,
        scenario_name="تقليل الإنفاق 10%",
        scenario_description="محاكاة خفض الإنفاق",
        baseline=sample_baseline_input(),
    )
    assert result.archetype == ScenarioArchetype.SPENDING_REDUCTION
    assert result.reduction_percent == 10.0


def test_index_assumptions_rejects_missing_dict_fields() -> None:
    with pytest.raises(SnapshotAdapterError) as exc:
        ScenarioAssumptionsAdapter._index_assumptions([{"label": "نسبة خفض الإنفاق"}])
    assert exc.value.error_code == "invalid_assumption"


def test_index_assumptions_rejects_missing_simulation_assumption_fields() -> None:
    with pytest.raises(SnapshotAdapterError) as exc:
        ScenarioAssumptionsAdapter._index_assumptions(
            [
                SimulationAssumption(
                    scenario_id=uuid.uuid4(),
                    label="نسبة خفض الإنفاق",
                    value="10%",
                ),
                SimulationAssumption(
                    scenario_id=uuid.uuid4(),
                    label="",
                    value="ignored",
                ),
            ]
        )
    assert exc.value.error_code == "invalid_assumption"


def test_rejects_missing_assumptions() -> None:
    with pytest.raises(SnapshotAdapterError) as exc:
        ScenarioAssumptionsAdapter().adapt(
            [],
            scenario_name="test",
            scenario_description="test",
            baseline=sample_baseline_input(),
        )
    assert exc.value.error_code == "missing_assumptions"
