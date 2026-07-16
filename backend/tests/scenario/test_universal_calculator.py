"""Universal AI-native scenario calculator tests (Sprint 5)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.business.engines.scenario.input import ScenarioBaselineInput, ScenarioCategoryBaseline
from app.business.engines.scenario.universal_calculator import (
    UniversalScenarioCalculator,
    UniversalScenarioInput,
)
from app.scenario.ai_contract import InterpretedScenario, ScenarioAction


def _baseline() -> ScenarioBaselineInput:
    return ScenarioBaselineInput(
        total_baseline=10_000_000.0,
        categories=(
            ScenarioCategoryBaseline("marketing", 2_000_000.0),
            ScenarioCategoryBaseline("operations", 3_000_000.0),
            ScenarioCategoryBaseline("procurement", 2_500_000.0),
            ScenarioCategoryBaseline("hr", 1_500_000.0),
            ScenarioCategoryBaseline("finance", 1_000_000.0),
        ),
        generated_at=datetime(2026, 7, 15, tzinfo=UTC),
    )


def _run(interpreted: InterpretedScenario) -> float:
    result = UniversalScenarioCalculator().calculate(
        UniversalScenarioInput(
            interpreted=interpreted,
            baseline=_baseline(),
            user_request="test",
        )
    )
    return result.projected_total


def _scenario(
    scenario_type: str,
    actions: list[ScenarioAction],
    *,
    target_amount: float | None = None,
) -> InterpretedScenario:
    return InterpretedScenario(
        scenario_type=scenario_type,
        title_ar=f"سيناريو {scenario_type}",
        summary_ar="اختبار",
        target_amount=target_amount,
        actions=actions,
        assumptions=["افتراض اختبار"],
        confidence=80,
    )


@pytest.mark.parametrize(
    ("scenario_type", "actions", "target_amount"),
    [
        (
            "increase_profit",
            [
                ScenarioAction(
                    action_type="increase_profit",
                    mode="absolute",
                    amount=200_000,
                    description="رفع الأرباح 200 ألف",
                )
            ],
            200_000,
        ),
        (
            "reduce_marketing_budget",
            [
                ScenarioAction(
                    action_type="reduce_budget",
                    mode="percent",
                    value=15,
                    category="marketing",
                    description="خفض ميزانية التسويق 15%",
                )
            ],
            None,
        ),
        (
            "close_branches",
            [
                ScenarioAction(
                    action_type="close_branches",
                    mode="count",
                    value=2,
                    description="إغلاق فرعين",
                )
            ],
            None,
        ),
        (
            "increase_payroll",
            [
                ScenarioAction(
                    action_type="increase_payroll",
                    mode="percent",
                    value=8,
                    department="hr",
                    description="رفع الرواتب 8%",
                )
            ],
            None,
        ),
        (
            "reduce_suppliers",
            [
                ScenarioAction(
                    action_type="reduce_suppliers",
                    mode="percent",
                    value=12,
                    description="خفض تكلفة الموردين",
                )
            ],
            None,
        ),
        (
            "increase_prices",
            [
                ScenarioAction(
                    action_type="increase_prices",
                    mode="percent",
                    value=3,
                    description="رفع الأسعار 3%",
                )
            ],
            None,
        ),
        (
            "reduce_waste",
            [
                ScenarioAction(
                    action_type="reduce_waste",
                    mode="percent",
                    value=40,
                    description="تقليل الهدر 40%",
                )
            ],
            None,
        ),
        (
            "hire_employees",
            [
                ScenarioAction(
                    action_type="hire_employees",
                    mode="count",
                    value=20,
                    amount=50_000,
                    department="hr",
                    description="توظيف 20 موظفاً",
                )
            ],
            None,
        ),
        (
            "investment",
            [
                ScenarioAction(
                    action_type="investment",
                    mode="absolute",
                    amount=1_000_000,
                    category="marketing",
                    description="رفع ميزانية التسويق مليون",
                )
            ],
            None,
        ),
        (
            "mixed",
            [
                ScenarioAction(
                    action_type="reduce_expense",
                    mode="percent",
                    value=10,
                    category="operations",
                    description="خفض العمليات 10%",
                ),
                ScenarioAction(
                    action_type="increase_revenue",
                    mode="percent",
                    value=5,
                    description="زيادة الإيرادات 5%",
                ),
            ],
            None,
        ),
    ],
)
def test_universal_calculator_executes_distinct_scenarios(
    scenario_type: str,
    actions: list[ScenarioAction],
    target_amount: float | None,
) -> None:
    projected = _run(_scenario(scenario_type, actions, target_amount=target_amount))
    assert projected > 0
    assert projected != 10_000_000.0


def test_distinct_scenarios_produce_different_totals() -> None:
    cases = [
        _scenario(
            "reduce_marketing",
            [
                ScenarioAction(
                    action_type="reduce_budget",
                    mode="percent",
                    value=15,
                    category="marketing",
                    description="",
                )
            ],
        ),
        _scenario(
            "close_branches",
            [ScenarioAction(action_type="close_branches", mode="count", value=2, description="")],
        ),
        _scenario(
            "increase_payroll",
            [
                ScenarioAction(
                    action_type="increase_payroll",
                    mode="percent",
                    value=8,
                    department="hr",
                    description="",
                )
            ],
        ),
    ]
    totals = {_run(item) for item in cases}
    assert len(totals) == 3
