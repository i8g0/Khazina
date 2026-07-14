"""ScenarioSnapshotAdapterV1 tests."""

from __future__ import annotations

import pytest

from app.decision.exceptions import SnapshotAdapterError
from app.scenario.adapters.snapshot_v1 import ScenarioSnapshotAdapterV1
from tests.scenario.conftest import sample_scenario_snapshot_payload


def test_adapt_baseline_from_snapshot() -> None:
    baseline = ScenarioSnapshotAdapterV1().adapt(sample_scenario_snapshot_payload())
    assert baseline.total_baseline == 48_750_000.0
    assert len(baseline.categories) == 3


def test_rejects_ambiguous_layout() -> None:
    payload = sample_scenario_snapshot_payload()
    payload["sheets"].append(payload["sheets"][0].copy())
    payload["sheets"][1]["name"] = "OtherDepartments"
    with pytest.raises(SnapshotAdapterError) as exc:
        ScenarioSnapshotAdapterV1().adapt(payload)
    assert exc.value.error_code == "ambiguous_layout"
