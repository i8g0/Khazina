"""Facts Contract unit tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.business.facts.contract import CONTRACT_VERSION, Fact, FactsContract


def test_fact_round_trip_serialization() -> None:
    fact = Fact(
        domain="waste",
        metric="waste.percentage",
        value="4.80",
        unit="percent",
        severity="medium",
        source="waste:waste_analysis",
        organization_id="org-1",
        period="2026-Q2",
        metadata={"category_name": "operations"},
    )
    restored = Fact.from_dict(fact.to_dict())
    assert restored == fact


def test_facts_contract_immutable_and_serializable() -> None:
    generated_at = datetime(2026, 7, 13, 12, 0, tzinfo=UTC)
    fact = Fact(
        domain="waste",
        metric="waste.total_amount",
        value="2340000.00",
        unit="currency",
        source="waste:waste_analysis",
    )
    contract = FactsContract(
        contract_version=CONTRACT_VERSION,
        engine_id="waste",
        engine_version="1.0.0",
        generated_at=generated_at,
        facts=(fact,),
        extensions={"engine_name": "Financial Waste Engine"},
    )

    payload = contract.to_dict()
    restored = FactsContract.from_dict(payload)
    json_payload = contract.to_json()

    assert restored == contract
    assert '"contract_version": "1.0"' in json_payload
    assert payload["engine_id"] == "waste"
    assert len(payload["facts"]) == 1

    with pytest.raises(AttributeError):
        contract.facts = ()  # type: ignore[misc]
