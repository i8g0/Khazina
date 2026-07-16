"""Financial reality engine tests — Sprint 6 acceptance scenarios."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.business.engines.scenario.financial_reality import FinancialRealityEngine
from app.business.engines.scenario.input import ScenarioBaselineInput, ScenarioCategoryBaseline
from app.scenario.ai_contract import InterpretedScenario, ScenarioAction


def _demo_baseline() -> ScenarioBaselineInput:
    """Scale similar to Khazina_Demo_Dataset_v2 (~78.5M SAR spend)."""
    return ScenarioBaselineInput(
        total_baseline=78_500_000.0,
        categories=(
            ScenarioCategoryBaseline("operations", 22_000_000.0),
            ScenarioCategoryBaseline("procurement", 18_500_000.0),
            ScenarioCategoryBaseline("marketing", 12_000_000.0),
            ScenarioCategoryBaseline("hr", 10_500_000.0),
            ScenarioCategoryBaseline("finance", 8_000_000.0),
            ScenarioCategoryBaseline("logistics", 7_500_000.0),
        ),
        generated_at=datetime(2026, 7, 15, tzinfo=UTC),
    )


def _run(actions: list[ScenarioAction], *, horizon: int = 4) -> tuple[float, float | None]:
    interpreted = InterpretedScenario(
        scenario_type="test",
        title_ar="اختبار",
        summary_ar="اختبار واقع مالي",
        actions=actions,
        horizon_quarters=horizon,
        confidence=75,
    )
    calc, financial = FinancialRealityEngine().simulate(interpreted, _demo_baseline())
    rev = financial.revenue_impact.expected if financial.revenue_impact else None
    return calc.projected_total, rev


def test_100k_branch_never_produces_millions_in_revenue() -> None:
    """Acceptance: 100k investment must not yield multi-million revenue uplift."""
    _, revenue = _run(
        [
            ScenarioAction(
                action_type="investment",
                mode="absolute",
                amount=100_000,
                category="operations",
                description="فتح فرع بميزانية 100,000 ريال",
            )
        ]
    )
    assert revenue is not None
    assert revenue < 500_000, f"100k branch produced unrealistic revenue: {revenue:,.0f}"
    assert revenue < 78_500_000 * 0.01, "Revenue uplift exceeds 1% of baseline spend"


def test_10m_branch_scales_realistically() -> None:
    """Acceptance: 10M investment should scale but stay bounded."""
    projected, revenue = _run(
        [
            ScenarioAction(
                action_type="investment",
                mode="absolute",
                amount=10_000_000,
                category="operations",
                description="فتح فرع بميزانية 10M",
            )
        ]
    )
    assert projected > 78_500_000
    assert revenue is not None
    assert revenue <= 20_000_000, f"10M branch revenue too high: {revenue:,.0f}"


def test_increase_salaries_5_percent() -> None:
    projected, _ = _run(
        [
            ScenarioAction(
                action_type="increase_payroll",
                mode="percent",
                value=5,
                department="hr",
                description="زيادة الرواتب 5%",
            )
        ]
    )
    baseline = 78_500_000.0
    delta_pct = ((projected - baseline) / baseline) * 100
    assert 0.5 < delta_pct < 2.0, f"5% payroll on HR only should be ~0.67% total, got {delta_pct:.2f}%"


def test_reduce_transport_20_percent() -> None:
    projected, _ = _run(
        [
            ScenarioAction(
                action_type="reduce_transport",
                mode="percent",
                value=20,
                category="logistics",
                description="خفض تكلفة النقل 20%",
            )
        ]
    )
    assert projected < 78_500_000
    savings = 78_500_000 - projected
    assert 1_000_000 < savings < 2_500_000


def test_increase_marketing_budget_1m() -> None:
    projected, revenue = _run(
        [
            ScenarioAction(
                action_type="increase_budget",
                mode="absolute",
                amount=1_000_000,
                category="marketing",
                description="زيادة ميزانية التسويق مليون",
            )
        ]
    )
    assert projected == pytest.approx(79_500_000, rel=0.001)
    assert revenue is not None
    assert revenue < 2_000_000


def test_reduce_procurement_15_percent() -> None:
    projected, _ = _run(
        [
            ScenarioAction(
                action_type="reduce_suppliers",
                mode="percent",
                value=15,
                category="procurement",
                description="خفض المشتريات 15%",
            )
        ]
    )
    savings = 78_500_000 - projected
    assert 2_000_000 < savings < 3_500_000


def test_increase_revenue_not_percent_of_spend() -> None:
    """Old bug: 10% revenue = 7.8M from spend. New: capped vs implied revenue."""
    _, revenue = _run(
        [
            ScenarioAction(
                action_type="increase_revenue",
                mode="percent",
                value=10,
                description="زيادة الإيرادات 10%",
            )
        ]
    )
    assert revenue is not None
    assert revenue < 10_000_000, f"10% revenue growth should not exceed ~8M implied cap, got {revenue:,.0f}"


def test_validation_notes_when_values_clamped() -> None:
    interpreted = InterpretedScenario(
        scenario_type="test",
        title_ar="اختبار",
        summary_ar="اختبار",
        actions=[
            ScenarioAction(
                action_type="increase_revenue",
                mode="absolute",
                amount=50_000_000,
                description="إيرادات مبالغ فيها",
            )
        ],
        confidence=80,
    )
    _, financial = FinancialRealityEngine().simulate(interpreted, _demo_baseline())
    assert financial.validation_notes
    assert financial.revenue_impact is not None
    assert financial.revenue_impact.expected < 50_000_000


def test_forecast_ranges_present() -> None:
    interpreted = InterpretedScenario(
        scenario_type="test",
        title_ar="اختبار",
        summary_ar="اختبار",
        actions=[
            ScenarioAction(
                action_type="investment",
                mode="absolute",
                amount=500_000,
                category="marketing",
                description="استثمار",
            )
        ],
        confidence=70,
    )
    _, financial = FinancialRealityEngine().simulate(interpreted, _demo_baseline())
    assert financial.cash_impact.worst <= financial.cash_impact.expected <= financial.cash_impact.best
    assert financial.confidence_level in {"high", "medium", "low"}
    assert financial.action_reasonings
