"""Sprint 6 financial reality proof — run without AI provider."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))

from app.business.engines.scenario.input import ScenarioBaselineInput, ScenarioCategoryBaseline
from app.business.engines.scenario.universal_calculator import (
    UniversalScenarioCalculator,
    UniversalScenarioInput,
)
from app.scenario.ai_contract import InterpretedScenario, ScenarioAction

DEMO_SPEND = 78_500_000.0


def _baseline() -> ScenarioBaselineInput:
    return ScenarioBaselineInput(
        total_baseline=DEMO_SPEND,
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


def _proof(label: str, actions: list[ScenarioAction]) -> None:
    interpreted = InterpretedScenario(
        scenario_type="proof",
        title_ar=label,
        summary_ar=label,
        actions=actions,
        confidence=75,
    )
    outcome = UniversalScenarioCalculator().calculate(
        UniversalScenarioInput(
            interpreted=interpreted,
            baseline=_baseline(),
            user_request=label,
        )
    )
    fin = outcome.financial_reality
    rev = fin.revenue_impact.expected if fin.revenue_impact else 0.0
    print(f"\n=== {label} ===")
    print(f"  Expense: {fin.expense_baseline:,.0f} -> {fin.expense_projected:,.0f} SAR")
    print(f"  Revenue (expected): {rev:,.0f} SAR")
    if fin.revenue_impact:
        print(
            f"  Revenue range: {fin.revenue_impact.worst:,.0f} / "
            f"{fin.revenue_impact.expected:,.0f} / {fin.revenue_impact.best:,.0f}"
        )
    print(f"  Confidence: {fin.confidence_level} ({fin.confidence_score}/100)")
    if fin.action_reasonings:
        print(f"  Reasoning: {fin.action_reasonings[0]}")


def main() -> None:
    print("Sprint 6 Financial Reality Proof (demo scale ~78.5M SAR)")
    print("OLD BUG: 100k branch -> ~7.36M revenue (10% of spend)")
    _proof(
        "افتح فرعاً بميزانية 100,000 ريال",
        [
            ScenarioAction(
                action_type="investment",
                mode="absolute",
                amount=100_000,
                category="operations",
                description="فتح فرع",
            )
        ],
    )
    _proof(
        "افتح فرعاً بميزانية 10,000,000 ريال",
        [
            ScenarioAction(
                action_type="investment",
                mode="absolute",
                amount=10_000_000,
                category="operations",
                description="فتح فرع كبير",
            )
        ],
    )
    _proof(
        "زيادة الرواتب 5%",
        [
            ScenarioAction(
                action_type="increase_payroll",
                mode="percent",
                value=5,
                department="hr",
                description="رواتب",
            )
        ],
    )
    _proof(
        "خفض تكلفة النقل 20%",
        [
            ScenarioAction(
                action_type="reduce_transport",
                mode="percent",
                value=20,
                category="logistics",
                description="نقل",
            )
        ],
    )
    _proof(
        "زيادة ميزانية التسويق 1,000,000 ريال",
        [
            ScenarioAction(
                action_type="increase_budget",
                mode="absolute",
                amount=1_000_000,
                category="marketing",
                description="تسويق",
            )
        ],
    )
    _proof(
        "خفض المشتريات 15%",
        [
            ScenarioAction(
                action_type="reduce_suppliers",
                mode="percent",
                value=15,
                category="procurement",
                description="مشتريات",
            )
        ],
    )
    print("\nALL PROOFS COMPLETE")


if __name__ == "__main__":
    main()
