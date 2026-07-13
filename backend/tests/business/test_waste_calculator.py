"""Waste Calculator unit tests."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.business.engines.waste.calculator import WasteCalculator
from app.business.engines.waste.input import WasteCategoryInput, WasteEngineInput
from app.business.exceptions import ValidationError


def _sample_input() -> WasteEngineInput:
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


def test_waste_calculator_is_deterministic() -> None:
    calculator = WasteCalculator()
    input_data = _sample_input()

    first = calculator.calculate(input_data)
    second = calculator.calculate(input_data)

    assert first == second
    assert first.waste_percentage == Decimal("4.68")
    assert first.top_category_name == "finance"
    assert first.top_category_percentage == Decimal("45.94")
    assert first.potential_savings_amount == Decimal("1872000.00")
    assert first.active_savings_opportunities == 3


def test_waste_calculator_rejects_non_positive_spend() -> None:
    calculator = WasteCalculator()
    input_data = WasteEngineInput(
        total_spend=0,
        total_waste_amount=100,
        categories=(WasteCategoryInput("x", 100),),
    )
    with pytest.raises(ValidationError):
        calculator.calculate(input_data)
