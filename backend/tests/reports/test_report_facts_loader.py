"""Facts loader tests for reports."""

from __future__ import annotations

import pytest

from app.reports.exceptions import ReportBuilderError
from app.reports.facts_loader import load_facts_contract
from tests.reports.conftest import sample_scenario_facts, sample_waste_facts


def test_load_waste_facts() -> None:
    contract = load_facts_contract(
        {"facts_contract": sample_waste_facts().to_dict()}
    )
    assert contract.engine_id == "waste"


def test_load_scenario_facts() -> None:
    contract = load_facts_contract(
        {"facts_contract": sample_scenario_facts().to_dict()}
    )
    assert contract.engine_id == "scenario"


def test_load_risk_facts() -> None:
    payload = sample_waste_facts().to_dict()
    payload["engine_id"] = "risk"
    contract = load_facts_contract({"facts_contract": payload})
    assert contract.engine_id == "risk"


def test_missing_facts_raises() -> None:
    with pytest.raises(ReportBuilderError) as exc:
        load_facts_contract({})
    assert exc.value.code == "missing_facts_contract"
