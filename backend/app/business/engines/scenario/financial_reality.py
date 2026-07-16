"""Financial reality engine — constrains simulation to dataset scale (Sprint 6)."""

from __future__ import annotations

from dataclasses import dataclass, field
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

MAX_ORGANIC_GROWTH_PCT_PER_YEAR = 5.0
MAX_PRICE_INCREASE_PCT = 12.0
MAX_EXPENSE_REDUCTION_PCT = 40.0
MAX_EXPENSE_INCREASE_PCT = 35.0
MAX_CATEGORY_CHANGE_PCT = 45.0
MAX_ANNUAL_ROI_ON_INVESTMENT = 1.2
MIN_ANNUAL_ROI_ON_INVESTMENT = 0.08
MAX_REVENUE_UPLIFT_VS_IMPLIED_PCT = 8.0
IMPLIED_REVENUE_TO_SPEND_RATIO = 1.05
HIRE_COST_DEFAULT_SAR = 85_000.0
BRANCH_CLOSE_SAVINGS_PCT_EACH = 2.5
BRANCH_CLOSE_SAVINGS_CAP_PCT = 12.0


def _money(value: float) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _clamp(value: float, low: float, high: float) -> float:
    return _money(max(low, min(high, value)))


@dataclass(frozen=True, slots=True)
class MetricRange:
    worst: float
    expected: float
    best: float
    label: str = ""

    def to_dict(self) -> dict[str, float | str]:
        return {
            "worst": self.worst,
            "expected": self.expected,
            "best": self.best,
            "label": self.label,
        }


@dataclass(frozen=True, slots=True)
class RealisticFinancialOutcome:
    expense_baseline: float
    expense_projected: float
    expense_change: MetricRange
    revenue_impact: MetricRange | None
    cash_impact: MetricRange
    confidence_level: str
    confidence_score: int
    confidence_rationale: str
    action_reasonings: tuple[str, ...]
    validation_notes: tuple[str, ...]
    assumptions_used: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "expense_baseline": self.expense_baseline,
            "expense_projected": self.expense_projected,
            "expense_change": self.expense_change.to_dict(),
            "revenue_impact": self.revenue_impact.to_dict() if self.revenue_impact else None,
            "cash_impact": self.cash_impact.to_dict(),
            "confidence_level": self.confidence_level,
            "confidence_score": self.confidence_score,
            "confidence_rationale": self.confidence_rationale,
            "action_reasonings": list(self.action_reasonings),
            "validation_notes": list(self.validation_notes),
            "assumptions_used": list(self.assumptions_used),
        }


@dataclass
class _FinancialState:
    category_amounts: dict[str, float]
    total_spend: float
    implied_annual_revenue: float
    revenue_expected: float = 0.0
    revenue_worst: float = 0.0
    revenue_best: float = 0.0
    total_investment: float = 0.0
    reasonings: list[str] = field(default_factory=list)
    validations: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    confidence_penalty: int = 0


_CATEGORY_ALIASES: dict[str, tuple[str, ...]] = {
    "finance": ("finance", "financial", "المالية", "الشؤون المالية"),
    "marketing": ("marketing", "التسويق"),
    "operations": ("operations", "operational", "العمليات", "التشغيل"),
    "procurement": ("procurement", "purchasing", "المشتريات"),
    "it": ("it", "technology", "تقنية", "تكنولوجيا"),
    "hr": ("hr", "human_resources", "payroll", "الموارد البشرية", "رواتب"),
    "travel": ("travel", "السفر"),
    "logistics": ("logistics", "transport", "shipping", "النقل", "الشحن"),
    "legal": ("legal", "compliance", "القانون", "الامتثال"),
    "facilities": ("facilities", "utilities", "administration", "المرافق", "الإدارة"),
    "overlapping_contracts": ("contracts", "overlapping_contracts", "العقود"),
}


class FinancialRealityEngine:
    """CFO-grade simulation: expenses and revenue constrained by uploaded baseline."""

    def simulate(
        self,
        interpreted: InterpretedScenario,
        baseline: ScenarioBaselineInput,
    ) -> tuple[ScenarioCalculationResult, RealisticFinancialOutcome]:
        timestamp = baseline.generated_at or datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        category_amounts = {c.category_name: float(c.amount) for c in baseline.categories}
        if not category_amounts:
            raise ValidationError("Baseline must contain at least one category")

        total_spend = _money(baseline.total_baseline)
        implied_revenue = _money(total_spend * IMPLIED_REVENUE_TO_SPEND_RATIO)
        horizon = interpreted.horizon_quarters
        horizon_years = max(horizon / 4.0, 0.25)

        state = _FinancialState(
            category_amounts=category_amounts,
            total_spend=total_spend,
            implied_annual_revenue=implied_revenue,
            assumptions=list(interpreted.assumptions),
        )
        state.assumptions.append(
            f"إيرادات تقديرية سنوية = {implied_revenue:,.0f} ر.س "
            f"({IMPLIED_REVENUE_TO_SPEND_RATIO:.0%} من إجمالي الإنفاق التشغيلي)"
        )

        for action in interpreted.actions:
            self._apply_action(state, action, horizon_years)

        self._validate_and_clamp(state, horizon_years)

        expense_projected = _money(sum(state.category_amounts.values()))
        expense_delta = _money(expense_projected - total_spend)
        expense_delta_pct = _money((expense_delta / total_spend) * 100) if total_spend else 0.0

        rev = MetricRange(
            worst=_money(state.revenue_worst),
            expected=_money(state.revenue_expected),
            best=_money(state.revenue_best),
            label="تأثير الإيرادات",
        )
        rev_range: MetricRange | None = rev if state.revenue_expected else None

        cash_expected = _money(rev.expected - expense_delta)
        cash_range = MetricRange(
            worst=_money(rev.worst - max(expense_delta, 0)),
            expected=cash_expected,
            best=_money(rev.best - min(expense_delta, 0)),
            label="الأثر على السيولة",
        )

        expense_range = MetricRange(
            worst=_money(min(expense_delta, 0) * 1.15),
            expected=expense_delta,
            best=_money(max(expense_delta, 0) * 1.1 if expense_delta > 0 else expense_delta * 0.85),
            label="تغير الإنفاق",
        )

        confidence_score = max(25, min(95, interpreted.confidence - state.confidence_penalty))
        confidence_level = (
            "high" if confidence_score >= 75 else "medium" if confidence_score >= 50 else "low"
        )
        confidence_rationale = self._confidence_rationale(state, confidence_level, confidence_score)

        categories = self._category_outcomes(baseline, state.category_amounts)
        comparison = self._comparison_metrics(
            interpreted,
            total_spend,
            expense_projected,
            expense_delta_pct,
            rev_range,
            cash_range,
            confidence_level,
        )
        chart_points = self._chart_points(total_spend, expense_projected, horizon)

        calculation = ScenarioCalculationResult(
            archetype=ScenarioArchetype.SPENDING_REDUCTION,
            baseline_total=total_spend,
            projected_total=expense_projected,
            delta_amount=expense_delta,
            delta_percent=expense_delta_pct,
            horizon_quarters=horizon,
            confidence_percent=confidence_score,
            categories=categories,
            comparison_metrics=comparison,
            chart_points=chart_points,
            organization_id=baseline.organization_id,
            period=baseline.period,
            source_dataset=baseline.source_dataset,
            generated_at=timestamp,
        )

        financial = RealisticFinancialOutcome(
            expense_baseline=total_spend,
            expense_projected=expense_projected,
            expense_change=expense_range,
            revenue_impact=rev_range,
            cash_impact=cash_range,
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            confidence_rationale=confidence_rationale,
            action_reasonings=tuple(state.reasonings),
            validation_notes=tuple(state.validations),
            assumptions_used=tuple(state.assumptions),
        )
        return calculation, financial

    def _apply_action(self, state: _FinancialState, action: ScenarioAction, horizon_years: float) -> None:
        at = action.action_type
        if at in {"reduce_expense", "reduce_budget", "reduce_waste", "reduce_transport", "reduce_suppliers"}:
            self._apply_expense_pct(state, action, reduce=True)
        elif at in {"increase_budget", "hire_employees", "increase_payroll", "investment"}:
            if at == "increase_payroll" and action.mode == "percent":
                self._apply_expense_pct(state, action, reduce=False)
            elif action.mode == "percent" and action.value is not None and at == "increase_budget":
                self._apply_expense_pct(state, action, reduce=False)
            else:
                self._apply_expense_increase(state, action, horizon_years)
        elif at == "increase_revenue":
            self._apply_revenue_growth(state, action, horizon_years)
        elif at == "increase_prices":
            self._apply_price_increase(state, action, horizon_years)
        elif at == "increase_profit":
            self._apply_profit_target(state, action)
        elif at == "close_branches":
            self._apply_branch_closure(state, action)
        elif at == "operational_change":
            pct = action.value if action.value is not None else 3.0
            wrapped = ScenarioAction(
                action_type="reduce_expense",
                mode="percent",
                value=min(pct, MAX_EXPENSE_REDUCTION_PCT),
                category=action.category,
                description=action.description,
            )
            self._apply_expense_pct(state, wrapped, reduce=True)
        elif at != "mixed":
            self._apply_expense_pct(state, action, reduce=True)

    def _apply_expense_pct(self, state: _FinancialState, action: ScenarioAction, *, reduce: bool) -> None:
        pct = action.value if action.mode == "percent" and action.value is not None else None
        if pct is None and action.mode == "absolute":
            amount = action.amount or action.value or 0.0
            pct = (amount / state.total_spend) * 100 if state.total_spend else 0.0
        if pct is None:
            pct = 5.0
            state.confidence_penalty += 8
            state.assumptions.append("نسبة افتراضية 5% — لم تُحدد نسبة صريحة")

        cap = MAX_EXPENSE_REDUCTION_PCT if reduce else MAX_EXPENSE_INCREASE_PCT
        if pct > cap:
            state.validations.append(f"تم تعديل النسبة من {pct:.1f}% إلى {cap}% (حد واقعي)")
            pct = cap

        targets = self._resolve_categories(action, state.category_amounts) or list(state.category_amounts)
        for key in targets:
            current = state.category_amounts[key]
            change = current * (pct / 100.0)
            if reduce:
                change = min(change, current * (MAX_CATEGORY_CHANGE_PCT / 100.0))
                state.category_amounts[key] = _money(current - change)
            else:
                state.category_amounts[key] = _money(current + change)

        direction = "خفض" if reduce else "زيادة"
        state.reasonings.append(
            f"{direction} {pct:.1f}% على {', '.join(targets[:3])} — "
            f"من إجمالي إنفاق {state.total_spend:,.0f} ر.س"
        )

    def _apply_expense_increase(
        self, state: _FinancialState, action: ScenarioAction, horizon_years: float
    ) -> None:
        if action.mode == "count":
            unit = action.amount or HIRE_COST_DEFAULT_SAR
            count = action.value or 1.0
            amount = unit * count
            state.reasonings.append(
                f"تكلفة {count:.0f} × {unit:,.0f} ر.س = {amount:,.0f} ر.س (رواتب/تأسيس)"
            )
        else:
            amount = action.amount or action.value or 0.0
            if amount <= 0:
                state.confidence_penalty += 15
                return

        max_allowed = state.total_spend * (MAX_EXPENSE_INCREASE_PCT / 100.0)
        if amount > max_allowed:
            state.validations.append(
                f"تم تعديل الإنفاق من {amount:,.0f} إلى {max_allowed:,.0f} ر.س "
                f"(≤{MAX_EXPENSE_INCREASE_PCT}% من الإنفاق)"
            )
            amount = max_allowed

        state.total_investment += amount
        targets = self._resolve_categories(action, state.category_amounts)
        if not targets:
            keys = list(state.category_amounts)
            targets = [keys[0]]
        per_target = amount / len(targets)
        for key in targets:
            if key in state.category_amounts:
                state.category_amounts[key] = _money(state.category_amounts[key] + per_target)

        invest_ratio = (amount / state.total_spend) * 100
        annual_roi = _clamp(
            MIN_ANNUAL_ROI_ON_INVESTMENT + (amount / state.total_spend) * 8.0,
            MIN_ANNUAL_ROI_ON_INVESTMENT,
            MAX_ANNUAL_ROI_ON_INVESTMENT,
        )
        expected_rev = amount * annual_roi * horizon_years
        state.revenue_expected += expected_rev
        state.revenue_worst += expected_rev * 0.35
        state.revenue_best += expected_rev * 1.4

        state.reasonings.append(
            f"استثمار {amount:,.0f} ر.س ({invest_ratio:.2f}% من الإنفاق) — "
            f"إيرادات متوقعة {expected_rev:,.0f} ر.س على {horizon_years:.1f} سنة "
            f"(ROI ~{annual_roi:.0%}، وليس ملايين دون مبرر)"
        )

    def _apply_revenue_growth(self, state: _FinancialState, action: ScenarioAction, horizon_years: float) -> None:
        if action.mode == "absolute" and action.amount:
            requested = action.amount
            cap = state.implied_annual_revenue * (MAX_REVENUE_UPLIFT_VS_IMPLIED_PCT / 100.0) * horizon_years
            if requested > cap:
                state.validations.append(
                    f"تم تعديل الإيرادات من {requested:,.0f} إلى {cap:,.0f} ر.س "
                    f"(≤{MAX_REVENUE_UPLIFT_VS_IMPLIED_PCT}% من الإيرادات التقديرية)"
                )
                requested = cap
            state.revenue_expected += requested
            state.revenue_worst += requested * 0.5
            state.revenue_best += requested * 1.25
            state.reasonings.append(
                f"زيادة إيرادات {action.amount:,.0f} ر.س → {requested:,.0f} ر.س "
                f"مقيّدة بحجم المنشأة ({state.implied_annual_revenue:,.0f} ر.س)"
            )
            return

        pct = action.value if action.value is not None else MAX_ORGANIC_GROWTH_PCT_PER_YEAR
        if pct > MAX_ORGANIC_GROWTH_PCT_PER_YEAR:
            state.validations.append(
                f"نمو {pct:.1f}% → {MAX_ORGANIC_GROWTH_PCT_PER_YEAR}% (حد نمو عضوي سنوي)"
            )
            pct = MAX_ORGANIC_GROWTH_PCT_PER_YEAR

        uplift = state.implied_annual_revenue * (pct / 100.0) * horizon_years
        state.revenue_expected += uplift
        state.revenue_worst += uplift * 0.6
        state.revenue_best += uplift * 1.2
        state.reasonings.append(
            f"نمو إيرادات {pct:.1f}% على {state.implied_annual_revenue:,.0f} ر.س = {uplift:,.0f} ر.س "
            f"(وليس {state.total_spend * pct / 100:,.0f} ر.س من الإنفاق)"
        )

    def _apply_price_increase(self, state: _FinancialState, action: ScenarioAction, horizon_years: float) -> None:
        pct = action.value if action.value is not None else 3.0
        if pct > MAX_PRICE_INCREASE_PCT:
            state.validations.append(f"رفع أسعار {pct:.1f}% → {MAX_PRICE_INCREASE_PCT}%")
            pct = MAX_PRICE_INCREASE_PCT
        effective = pct * 0.65
        uplift = state.implied_annual_revenue * (effective / 100.0) * horizon_years
        state.revenue_expected += uplift
        state.revenue_worst += uplift * 0.5
        state.revenue_best += uplift * 1.15
        state.reasonings.append(f"رفع أسعار {pct:.1f}% → إيرادات ~{uplift:,.0f} ر.س (مرونة طلب 65%)")

    def _apply_profit_target(self, state: _FinancialState, action: ScenarioAction) -> None:
        target = action.amount or action.value
        if target is None:
            target = state.total_spend * 0.02
            state.confidence_penalty += 10
        max_cut = state.total_spend * 0.15
        cut_target = min(float(target), max_cut)
        if cut_target < float(target):
            state.validations.append(
                f"هدف ربح {target:,.0f} ر.س — خفض إنفاق حتى {cut_target:,.0f} ر.س فقط"
            )
        remaining = cut_target
        for key in sorted(state.category_amounts, key=lambda k: state.category_amounts[k], reverse=True):
            if remaining <= 0:
                break
            cut = min(state.category_amounts[key] * 0.25, remaining)
            state.category_amounts[key] = _money(state.category_amounts[key] - cut)
            remaining -= cut
        state.reasonings.append(f"هدف ربح {target:,.0f} ر.س عبر خفض إنفاق ≤{cut_target:,.0f} ر.س")

    def _apply_branch_closure(self, state: _FinancialState, action: ScenarioAction) -> None:
        branches = int(action.value or action.amount or 1)
        pct = min(branches * BRANCH_CLOSE_SAVINGS_PCT_EACH, BRANCH_CLOSE_SAVINGS_CAP_PCT)
        wrapped = ScenarioAction(
            action_type="reduce_expense",
            mode="percent",
            value=pct,
            category="operations",
            description=action.description,
        )
        self._apply_expense_pct(state, wrapped, reduce=True)
        state.reasonings.append(f"إغلاق {branches} فرع — توفير ~{pct:.1f}% على العمليات")

    def _validate_and_clamp(self, state: _FinancialState, horizon_years: float) -> None:
        max_rev = state.implied_annual_revenue * (
            MAX_REVENUE_UPLIFT_VS_IMPLIED_PCT / 100.0
        ) * horizon_years + state.total_investment * MAX_ANNUAL_ROI_ON_INVESTMENT * horizon_years
        if state.revenue_expected > max_rev:
            state.validations.append(
                f"إيرادات {state.revenue_expected:,.0f} → {max_rev:,.0f} ر.س (حد منطقي)"
            )
            ratio = max_rev / state.revenue_expected if state.revenue_expected else 1.0
            state.revenue_expected = _money(max_rev)
            state.revenue_worst = _money(state.revenue_worst * ratio)
            state.revenue_best = _money(min(state.revenue_best * ratio, max_rev * 1.3))
            state.confidence_penalty += 12

        if state.total_investment > 0 and state.revenue_expected > state.total_investment * 3 * horizon_years:
            cap = state.total_investment * 2 * horizon_years
            state.validations.append(f"ROI مبالغ — تعديل إيرادات إلى {cap:,.0f} ر.س")
            state.revenue_expected = min(state.revenue_expected, cap)
            state.confidence_penalty += 15

    @staticmethod
    def _confidence_rationale(state: _FinancialState, level: str, score: int) -> str:
        parts = [f"درجة الثقة {score}/100 ({level})"]
        if state.total_investment > 0:
            parts.append(f"استثمار {(state.total_investment / state.total_spend) * 100:.2f}% من الإنفاق")
        if state.validations:
            parts.append(f"{len(state.validations)} تعديل/قيد مالي")
        return " — ".join(parts)

    def _resolve_categories(self, action: ScenarioAction, category_amounts: dict[str, float]) -> list[str]:
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
    ) -> tuple[ScenarioCategoryOutcome, ...]:
        baseline_map = {item.category_name: item.amount for item in baseline.categories}
        outcomes: list[ScenarioCategoryOutcome] = []
        for name in sorted(projected_amounts):
            base_amt = _money(baseline_map.get(name, 0.0))
            proj_amt = _money(projected_amounts[name])
            change = _money(proj_amt - base_amt)
            if change < 0:
                direction = MetricDirection.DOWN
            elif change > 0:
                direction = MetricDirection.UP
            else:
                direction = MetricDirection.NEUTRAL
            outcomes.append(
                ScenarioCategoryOutcome(
                    category_name=name,
                    baseline_amount=base_amt,
                    projected_amount=proj_amt,
                    change_amount=change,
                    direction=direction,
                )
            )
        return tuple(outcomes)

    def _comparison_metrics(
        self,
        interpreted: InterpretedScenario,
        expense_baseline: float,
        expense_projected: float,
        expense_delta_pct: float,
        revenue: MetricRange | None,
        cash: MetricRange,
        confidence_level: str,
    ) -> tuple[ScenarioComparisonOutcome, ...]:
        sign = "+" if expense_delta_pct > 0 else ""
        if expense_delta_pct > 0:
            exp_dir = MetricDirection.UP
        elif expense_delta_pct < 0:
            exp_dir = MetricDirection.DOWN
        else:
            exp_dir = MetricDirection.NEUTRAL
        metrics: list[ScenarioComparisonOutcome] = [
            ScenarioComparisonOutcome(
                metric_name="إجمالي الإنفاق",
                current_value=self._format_amount(expense_baseline),
                simulated_value=self._format_amount(expense_projected),
                change_value=f"{sign}{expense_delta_pct:.1f}%",
                direction=exp_dir,
            ),
            ScenarioComparisonOutcome(
                metric_name="السيناريو",
                current_value="خط الأساس",
                simulated_value=interpreted.title_ar[:80],
                change_value=confidence_level,
                direction=MetricDirection.NEUTRAL,
            ),
        ]
        if revenue:
            metrics.append(
                ScenarioComparisonOutcome(
                    metric_name="تأثير الإيرادات (متوقع)",
                    current_value=self._format_amount(revenue.expected),
                    simulated_value=f"{self._format_amount(revenue.worst)} – {self._format_amount(revenue.best)}",
                    change_value="أسوأ – أفضل",
                    direction=MetricDirection.NEUTRAL,
                )
            )
        metrics.append(
            ScenarioComparisonOutcome(
                metric_name="الأثر على السيولة",
                current_value=self._format_amount(cash.expected),
                simulated_value=f"{self._format_amount(cash.worst)} – {self._format_amount(cash.best)}",
                change_value="نطاق",
                direction=MetricDirection.NEUTRAL,
            )
        )
        return tuple(metrics)

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
    def _format_amount(value: float) -> str:
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"{value / 1_000:.1f}K"
        return f"{value:.0f}"
