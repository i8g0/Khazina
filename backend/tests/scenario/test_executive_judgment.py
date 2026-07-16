"""Executive Financial Judgment Layer tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.business.engines.scenario.financial_reality import FinancialRealityEngine
from app.business.engines.scenario.input import ScenarioBaselineInput, ScenarioCategoryBaseline
from app.scenario.ai_contract import InterpretedScenario, ScenarioAction
from app.scenario.executive_judgment import RECOMMENDATION_LABELS_AR, build_executive_judgment


def _large_baseline() -> ScenarioBaselineInput:
    return ScenarioBaselineInput(
        total_baseline=285_000_000.0,
        categories=(
            ScenarioCategoryBaseline("marketing", 40_000_000.0),
            ScenarioCategoryBaseline("operations", 80_000_000.0),
            ScenarioCategoryBaseline("procurement", 65_000_000.0),
        ),
        generated_at=datetime(2026, 7, 15, tzinfo=UTC),
    )


def _run_judgment(
    actions: list[ScenarioAction],
    *,
    user_request: str,
    target_amount: float | None = None,
) -> tuple:
    interpreted = InterpretedScenario(
        scenario_type="increase_budget",
        title_ar="زيادة تسويق",
        summary_ar=user_request,
        target_amount=target_amount,
        actions=actions,
        horizon_quarters=4,
        confidence=75,
    )
    calc, financial = FinancialRealityEngine().simulate(interpreted, _large_baseline())
    from app.scenario.ai_contract import FinancialRealityPayload, MetricRangePayload

    fr = FinancialRealityPayload(
        expense_baseline=financial.expense_baseline,
        expense_projected=financial.expense_projected,
        expense_change=MetricRangePayload(**financial.expense_change.to_dict()),
        revenue_impact=(
            MetricRangePayload(**financial.revenue_impact.to_dict())
            if financial.revenue_impact
            else None
        ),
        cash_impact=MetricRangePayload(**financial.cash_impact.to_dict()),
        confidence_level=financial.confidence_level,
        confidence_score=financial.confidence_score,
        confidence_rationale=financial.confidence_rationale,
        action_reasonings=list(financial.action_reasonings),
        validation_notes=list(financial.validation_notes),
        assumptions_used=list(financial.assumptions_used),
    )
    judgment = build_executive_judgment(
        user_request=user_request,
        interpreted=interpreted,
        baseline=_large_baseline(),
        calculation=calc,
        financial_reality=fr,
    )
    return judgment, calc


def test_marketing_50k_is_immaterial_on_40m_budget() -> None:
    """50k on 40M marketing = 0.125% — immaterial, approve with modifications."""
    judgment, _ = _run_judgment(
        [
            ScenarioAction(
                action_type="increase_budget",
                mode="absolute",
                amount=50_000,
                category="marketing",
                description="زيادة التسويق",
            )
        ],
        user_request="زيادة ميزانية التسويق 50,000 ريال",
        target_amount=50_000,
    )
    assert "0.125" in judgment.materiality_analysis or "0.12" in judgment.materiality_analysis
    assert "غير جوهري" in judgment.materiality_analysis or "0.125" in judgment.materiality_analysis
    assert judgment.recommendation == RECOMMENDATION_LABELS_AR["approve_with_modifications"]
    assert "2–5%" in judgment.strategic_advice or "2-5%" in judgment.strategic_advice.replace("–", "-")


def test_10k_branch_rejected_on_large_company() -> None:
    """10k branch on 285M spend — not financially executable."""
    judgment, _ = _run_judgment(
        [
            ScenarioAction(
                action_type="investment",
                mode="absolute",
                amount=10_000,
                category="operations",
                description="فتح فرع",
            )
        ],
        user_request="افتح فرع جديد بميزانية 10,000 ريال",
        target_amount=10_000,
    )
    assert judgment.recommendation == RECOMMENDATION_LABELS_AR["reject"]
    assert "غير كافية" in judgment.financial_realism or "غير قابل" in judgment.financial_realism
    assert "0.00" in judgment.materiality_analysis or "0.004" in judgment.materiality_analysis


def test_judgment_includes_verdict_sections() -> None:
    judgment, _ = _run_judgment(
        [
            ScenarioAction(
                action_type="increase_budget",
                mode="absolute",
                amount=500_000,
                category="marketing",
            )
        ],
        user_request="زيادة التسويق 500 ألف",
        target_amount=500_000,
    )
    assert judgment.executive_verdict
    assert judgment.financial_justification
    assert judgment.strategic_recommendation
    assert judgment.confidence_statement
    assert judgment.alternative_option
    assert judgment.next_step
    assert len(judgment.supporting_indicators) >= 3
