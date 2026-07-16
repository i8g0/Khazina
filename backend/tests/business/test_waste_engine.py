"""Waste Engine lifecycle unit tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.business.engines.waste.engine import WasteEngine
from app.business.engines.waste.input import WasteCategoryInput, WasteEngineInput
from app.business.engines.waste.manifest import WASTE_ENGINE_MANIFEST
from app.business.exceptions import (
    BusinessRuleViolationError,
    InvalidInputError,
    MissingDataError,
    ValidationError,
)


def _valid_input() -> WasteEngineInput:
    return WasteEngineInput(
        total_spend=50_000_000.0,
        total_waste_amount=2_340_000.0,
        categories=(
            WasteCategoryInput("overlapping_contracts", 745_000.0),
            WasteCategoryInput("operations", 520_000.0),
            WasteCategoryInput("finance", 1_075_000.0),
        ),
        organization_id="org-123",
        period="2026-Q2",
        generated_at=datetime(2026, 7, 13, tzinfo=UTC),
    )


def test_waste_engine_lifecycle_returns_facts_contract() -> None:
    engine = WasteEngine()
    contract = engine.run(_valid_input())

    assert contract.engine_id == "waste"
    assert contract.engine_version == "1.0.0"
    assert contract.generated_at == datetime(2026, 7, 13, tzinfo=UTC)
    assert len(contract.facts) >= len(WASTE_ENGINE_MANIFEST.supported_facts)

    percentage = next(f for f in contract.facts if f.metric == "waste.percentage")
    assert percentage.value == "4.68"
    assert percentage.severity == "low"


def test_waste_engine_manifest_complete() -> None:
    manifest = WasteEngine().manifest
    assert manifest.engine_id == "waste"
    assert manifest.engine_name
    assert manifest.engine_version == "1.0.0"
    assert manifest.engine_description
    assert manifest.supported_facts
    assert manifest.extensions["facts_contract_version"] == "1.1"


@pytest.mark.parametrize(
    ("input_data", "expected"),
    [
        (
            WasteEngineInput(
                total_spend=0,
                total_waste_amount=100,
                categories=(WasteCategoryInput("x", 100),),
            ),
            ValidationError,
        ),
        (
            WasteEngineInput(
                total_spend=100,
                total_waste_amount=-1,
                categories=(WasteCategoryInput("x", -1),),
            ),
            ValidationError,
        ),
        (
            WasteEngineInput(
                total_spend=100,
                total_waste_amount=200,
                categories=(WasteCategoryInput("x", 200),),
            ),
            BusinessRuleViolationError,
        ),
        (
            WasteEngineInput(
                total_spend=100,
                total_waste_amount=100,
                categories=(),
            ),
            MissingDataError,
        ),
        ("not-input", InvalidInputError),
    ],
)
def test_waste_engine_validation_errors(input_data, expected) -> None:
    engine = WasteEngine()
    with pytest.raises(expected):
        engine.run(input_data)


def test_waste_engine_category_sum_mismatch() -> None:
    engine = WasteEngine()
    input_data = WasteEngineInput(
        total_spend=1000,
        total_waste_amount=100,
        categories=(WasteCategoryInput("x", 50),),
    )
    with pytest.raises(BusinessRuleViolationError):
        engine.run(input_data)
