"""ScenarioAssumptionsAdapter tests."""

from __future__ import annotations

import pytest

from app.business.engines.scenario.input import ScenarioArchetype
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


def test_rejects_missing_assumptions() -> None:
    with pytest.raises(SnapshotAdapterError) as exc:
        ScenarioAssumptionsAdapter().adapt(
            [],
            scenario_name="test",
            scenario_description="test",
            baseline=sample_baseline_input(),
        )
    assert exc.value.error_code == "missing_assumptions"
