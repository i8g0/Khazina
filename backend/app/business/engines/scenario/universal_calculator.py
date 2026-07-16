"""Universal AI-native scenario calculator — executes any valid interpreted scenario."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

from app.business.engines.scenario.calculator import (
    ScenarioCalculationResult,
    ScenarioCategoryOutcome,
    ScenarioChartOutcome,
    ScenarioComparisonOutcome,
)
from app.business.engines.scenario.input import ScenarioArchetype, ScenarioBaselineInput
from app.business.exceptions import ValidationError
from app.db.models.enums import MetricDirection
from app.scenario.ai_contract import InterpretedScenario, ScenarioAction

_CATEGORY_ALIASES: dict[str, tuple[str, ...]] = {
    "finance": ("finance", "financial", "المالية", "الشؤون المالية"),
    "marketing": ("marketing", "التسويق"),
    "operations": ("operations", "operational", "العمليات", "التشغيل"),
    "procurement": ("procurement", "purchasing", "المشتريات"),
    "it": ("it", "technology", "تقنية", "تكنولوجيا"),
    "hr": ("hr", "human_resources", "payroll", "الموارد البشرية", "رواتب"),
    "travel": ("travel", "السفر"),
    "logistics": ("logistics", "transport", "shipping", "اللوجستics", "النقل", "الشحن"),
    "legal": ("legal", "compliance", "القانون", "الامتثال"),
    "facilities": ("facilities", "utilities", "administration", "المرافق", "الإدارة"),
    "overlapping_contracts": ("contracts", "overlapping_contracts", "العقود"),
}


def _money(value: float) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@dataclass
class UniversalScenarioInput:
    interpreted: InterpretedScenario
    baseline: ScenarioBaselineInput
    user_request: str


class UniversalScenarioCalculator:
    """Applies AI-interpreted actions to financial baseline."""

    def calculate(self, input_data: UniversalScenarioInput) -> ScenarioCalculationResult:
        baseline = input_data.baseline
        interpreted = input_data.interpreted
        timestamp = baseline.generated_at or datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        category_amounts: dict[str, float] = {
            item.category_name: float(item.amount) for item in baseline.categories
        }
        if not category_amounts:
            raise ValidationError("Baseline must contain at least one category")

        revenue_uplift = 0.0
        for action in interpreted.actions:
            revenue_uplift += self._apply_action(action, category_amounts, baseline.total_baseline)

        baseline_total = _money(baseline.total_baseline)
        projected_total = _money(max(sum(category_amounts.values()) + revenue_uplift, baseline_total * 0.05))
        delta_amount = _money(projected_total - baseline_total)
        delta_percent = _money((delta_amount / baseline_total) * 100) if baseline_total else 0.0

        projected_factor = projected_total / baseline_total if baseline_total else 1.0
        categories = self._category_outcomes(baseline, category_amounts, projected_total)
        comparison = self._comparison_metrics(
            interpreted,
            baseline_total,
            projected_total,
            delta_percent,
            category_amounts,
            revenue_uplift,
        )
        chart_points = self._chart_points(
            baseline_total, projected_total, interpreted.horizon_quarters
        )

        return ScenarioCalculationResult(
            archetype=ScenarioArchetype.SPENDING_REDUCTION,
            baseline_total=baseline_total,
            projected_total=projected_total,
            delta_amount=delta_amount,
            delta_percent=delta_percent,
            horizon_quarters=interpreted.horizon_quarters,
            confidence_percent=interpreted.confidence,
            categories=categories,
            comparison_metrics=comparison,
            chart_points=chart_points,
            organization_id=baseline.organization_id,
            period=baseline.period,
            source_dataset=baseline.source_dataset,
            generated_at=timestamp,
        )

    def _apply_action(
        self,
        action: ScenarioAction,
        category_amounts: dict[str, float],
        baseline_total: float,
    ) -> float:
        action_type = action.action_type
        if action_type in {"reduce_expense", "reduce_budget", "reduce_waste", "reduce_transport"}:
            return self._apply_expense_change(action, category_amounts, baseline_total, reduce=True)
        if action_type in {"increase_budget", "hire_employees", "increase_payroll", "investment"}:
            return self._apply_expense_change(action, category_amounts, baseline_total, reduce=False)
        if action_type == "increase_revenue":
            return self._apply_revenue(action, baseline_total)
        if action_type == "increase_profit":
            return self._apply_profit(action, category_amounts, baseline_total)
        if action_type == "increase_prices":
            return self._apply_revenue(action, baseline_total, default_pct=3.0)
        if action_type == "reduce_suppliers":
            pct = action.value if action.mode == "percent" and action.value else 8.0
            return self._apply_overall_percent(category_amounts, baseline_total, pct, reduce=True, categories=("procurement", "overlapping_contracts"))
        if action_type == "close_branches":
            branches = int(action.value or action.amount or 1)
            pct = min(branches * 4.5, 25.0)
            return self._apply_overall_percent(
                category_amounts,
                baseline_total,
                pct,
                reduce=True,
                categories=("operations", "facilities"),
            )
        if action_type == "operational_change":
            pct = action.value if action.value else 5.0
            return self._apply_overall_percent(category_amounts, baseline_total, pct, reduce=True)
        if action_type == "mixed":
            return 0.0
        return self._apply_expense_change(action, category_amounts, baseline_total, reduce=True)

    def _apply_expense_change(
        self,
        action: ScenarioAction,
        category_amounts: dict[str, float],
        baseline_total: float,
        *,
        reduce: bool,
    ) -> float:
        targets = self._resolve_categories(action, category_amounts)
        if not targets:
            targets = list(category_amounts.keys())

        delta_total = 0.0
        for key in targets:
            current = category_amounts[key]
            change = self._change_amount(action, current, baseline_total)
            if reduce:
                change = min(change, current * 0.95)
                category_amounts[key] = _money(current - change)
                delta_total -= change
            else:
                category_amounts[key] = _money(current + change)
                delta_total += change
        return 0.0

    def _apply_revenue(
        self, action: ScenarioAction, baseline_total: float, *, default_pct: float = 10.0
    ) -> float:
        if action.mode == "absolute" and action.amount:
            return _money(action.amount)
        pct = action.value if action.value is not None else default_pct
        return _money(baseline_total * (pct / 100.0))

    def _apply_profit(
        self,
        action: ScenarioAction,
        category_amounts: dict[str, float],
        baseline_total: float,
    ) -> float:
        target = action.amount or action.value
        if target is None and action.mode == "absolute":
            target = 0.0
        if target is None:
            target = baseline_total * 0.03
        remaining = float(target)
        sorted_keys = sorted(category_amounts, key=lambda k: category_amounts[k], reverse=True)
        for key in sorted_keys:
            if remaining <= 0:
                break
            cut = min(category_amounts[key] * 0.4, remaining)
            category_amounts[key] = _money(category_amounts[key] - cut)
            remaining -= cut
        return 0.0

    def _apply_overall_percent(
        self,
        category_amounts: dict[str, float],
        baseline_total: float,
        pct: float,
        *,
        reduce: bool,
        categories: tuple[str, ...] = (),
    ) -> float:
        keys = [k for k in category_amounts if not categories or self._matches_category(k, categories)]
        if not keys:
            keys = list(category_amounts.keys())
        for key in keys:
            current = category_amounts[key]
            change = current * (pct / 100.0)
            category_amounts[key] = _money(current - change if reduce else current + change)
        return 0.0

    @staticmethod
    def _change_amount(action: ScenarioAction, current: float, baseline_total: float) -> float:
        if action.mode == "absolute":
            return _money(action.amount or action.value or 0.0)
        if action.mode == "count":
            unit = action.amount or 50_000.0
            count = action.value or 1.0
            return _money(unit * count)
        pct = action.value if action.value is not None else 10.0
        return _money(current * (pct / 100.0))

    def _resolve_categories(
        self, action: ScenarioAction, category_amounts: dict[str, float]
    ) -> list[str]:
        needle = (action.category or action.department or "").strip().lower()
        if not needle:
            return []
        matched: list[str] = []
        for key in category_amounts:
            if self._matches_category(key, (needle,)):
                matched.append(key)
        if matched:
            return matched
        for canonical, aliases in _CATEGORY_ALIASES.items():
            if needle == canonical or needle in aliases:
                for key in category_amounts:
                    if self._matches_category(key, (canonical, *aliases)):
                        matched.append(key)
        return matched

    @staticmethod
    def _matches_category(category_key: str, needles: tuple[str, ...]) -> bool:
        normalized = category_key.strip().lower().replace("_", " ")
        for needle in needles:
            n = needle.strip().lower().replace("_", " ")
            if n and (n in normalized or normalized in n):
                return True
        return False

    @staticmethod
    def _category_outcomes(
        baseline: ScenarioBaselineInput,
        projected_amounts: dict[str, float],
        projected_total: float,
    ) -> tuple[ScenarioCategoryOutcome, ...]:
        outcomes: list[ScenarioCategoryOutcome] = []
        baseline_map = {item.category_name: item.amount for item in baseline.categories}
        for name in sorted(projected_amounts):
            base_amt = _money(baseline_map.get(name, 0.0))
            proj_amt = _money(projected_amounts[name])
            change = _money(proj_amt - base_amt)
            direction = UniversalScenarioCalculator._direction(change)
            outcomes.append(
                ScenarioCategoryOutcome(
                    category_name=name,
                    baseline_amount=base_amt,
                    projected_amount=proj_amt,
                    change_amount=change,
                    direction=direction,
                )
            )
        if not outcomes and baseline.categories:
            share_total = sum(item.amount for item in baseline.categories) or baseline.total_baseline
            for item in baseline.categories:
                share = item.amount / share_total if share_total else 0.0
                proj_amt = _money(projected_total * share)
                change = _money(proj_amt - item.amount)
                outcomes.append(
                    ScenarioCategoryOutcome(
                        category_name=item.category_name,
                        baseline_amount=_money(item.amount),
                        projected_amount=proj_amt,
                        change_amount=change,
                        direction=UniversalScenarioCalculator._direction(change),
                    )
                )
        return tuple(outcomes)

    @staticmethod
    def _comparison_metrics(
        interpreted: InterpretedScenario,
        baseline_total: float,
        projected_total: float,
        delta_percent: float,
        category_amounts: dict[str, float],
        revenue_uplift: float,
    ) -> tuple[ScenarioComparisonOutcome, ...]:
        direction = UniversalScenarioCalculator._direction(projected_total - baseline_total)
        change = UniversalScenarioCalculator._format_percent(delta_percent)
        gross_revenue = baseline_total + revenue_uplift
        return (
            ScenarioComparisonOutcome(
                metric_name="إجمالي الإنفاق",
                current_value=UniversalScenarioCalculator._format_amount(baseline_total),
                simulated_value=UniversalScenarioCalculator._format_amount(projected_total),
                change_value=change,
                direction=direction,
            ),
            ScenarioComparisonOutcome(
                metric_name="السيناريو",
                current_value="خط الأساس",
                simulated_value=interpreted.title_ar[:80],
                change_value=interpreted.scenario_type,
                direction=MetricDirection.NEUTRAL,
            ),
            ScenarioComparisonOutcome(
                metric_name="الأثر على الإيرادات",
                current_value=UniversalScenarioCalculator._format_amount(baseline_total),
                simulated_value=UniversalScenarioCalculator._format_amount(gross_revenue),
                change_value=UniversalScenarioCalculator._format_amount(revenue_uplift),
                direction=UniversalScenarioCalculator._direction(revenue_uplift),
            ),
        )

    @staticmethod
    def _chart_points(
        baseline_total: float, projected_total: float, horizon_quarters: int
    ) -> tuple[ScenarioChartOutcome, ...]:
        labels = ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12")
        per_baseline = _money(baseline_total / horizon_quarters)
        per_projected = _money(projected_total / horizon_quarters)
        return tuple(
            ScenarioChartOutcome(
                quarter_label=labels[index],
                quarter_order=index + 1,
                baseline_amount=per_baseline,
                projected_amount=per_projected,
            )
            for index in range(min(horizon_quarters, len(labels)))
        )

    @staticmethod
    def _direction(change: float) -> str:
        if change > 0:
            return MetricDirection.UP
        if change < 0:
            return MetricDirection.DOWN
        return MetricDirection.NEUTRAL

    @staticmethod
    def _format_amount(value: float) -> str:
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"{value / 1_000:.1f}K"
        return f"{value:.0f}"

    @staticmethod
    def _format_percent(value: float) -> str:
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.1f}%"
