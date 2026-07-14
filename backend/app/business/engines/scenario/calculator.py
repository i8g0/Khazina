"""Scenario Engine deterministic calculations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

from app.business.engines.scenario.input import (
    ScenarioArchetype,
    ScenarioBaselineInput,
    ScenarioEngineInput,
)
from app.business.exceptions import BusinessRuleViolationError, ValidationError
from app.db.models.enums import MetricDirection


def _money(value: float) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@dataclass(frozen=True, slots=True)
class ScenarioCategoryOutcome:
    category_name: str
    baseline_amount: float
    projected_amount: float
    change_amount: float
    direction: str


@dataclass(frozen=True, slots=True)
class ScenarioComparisonOutcome:
    metric_name: str
    current_value: str
    simulated_value: str
    change_value: str
    direction: str


@dataclass(frozen=True, slots=True)
class ScenarioChartOutcome:
    quarter_label: str
    quarter_order: int
    baseline_amount: float
    projected_amount: float


@dataclass(frozen=True, slots=True)
class ScenarioCalculationResult:
    archetype: ScenarioArchetype
    baseline_total: float
    projected_total: float
    delta_amount: float
    delta_percent: float
    horizon_quarters: int
    confidence_percent: int
    categories: tuple[ScenarioCategoryOutcome, ...]
    comparison_metrics: tuple[ScenarioComparisonOutcome, ...]
    chart_points: tuple[ScenarioChartOutcome, ...]
    organization_id: str | None
    period: str | None
    source_dataset: str
    generated_at: datetime


class ScenarioCalculator:
    """Applies archetype formulas to baseline financial inputs."""

    _CONFIDENCE_BY_ARCHETYPE = {
        ScenarioArchetype.SPENDING_REDUCTION: 88,
        ScenarioArchetype.SUPPLIER_CONSOLIDATION: 85,
        ScenarioArchetype.MARKET_EXPANSION: 72,
    }

    def calculate(self, input_data: ScenarioEngineInput) -> ScenarioCalculationResult:
        baseline = input_data.baseline
        timestamp = baseline.generated_at or datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        if input_data.archetype == ScenarioArchetype.SPENDING_REDUCTION:
            projected_factor = self._spending_reduction_factor(input_data)
        elif input_data.archetype == ScenarioArchetype.SUPPLIER_CONSOLIDATION:
            projected_factor = self._supplier_consolidation_factor(input_data)
        else:
            projected_total = self._market_expansion_total(input_data)
            projected_factor = (
                projected_total / baseline.total_baseline
                if baseline.total_baseline
                else 0.0
            )

        baseline_total = _money(baseline.total_baseline)
        if input_data.archetype == ScenarioArchetype.MARKET_EXPANSION:
            projected_total = _money(projected_total)
        else:
            projected_total = _money(baseline_total * projected_factor)

        delta_amount = _money(projected_total - baseline_total)
        delta_percent = (
            _money((delta_amount / baseline_total) * 100) if baseline_total else 0.0
        )

        categories = self._category_outcomes(baseline, projected_factor, projected_total)
        comparison = self._comparison_metrics(
            input_data, baseline_total, projected_total, delta_percent
        )
        chart_points = self._chart_points(
            baseline_total, projected_total, input_data.horizon_quarters
        )

        return ScenarioCalculationResult(
            archetype=input_data.archetype,
            baseline_total=baseline_total,
            projected_total=projected_total,
            delta_amount=delta_amount,
            delta_percent=delta_percent,
            horizon_quarters=input_data.horizon_quarters,
            confidence_percent=self._CONFIDENCE_BY_ARCHETYPE[input_data.archetype],
            categories=categories,
            comparison_metrics=comparison,
            chart_points=chart_points,
            organization_id=baseline.organization_id,
            period=baseline.period,
            source_dataset=baseline.source_dataset,
            generated_at=timestamp,
        )

    @staticmethod
    def _spending_reduction_factor(input_data: ScenarioEngineInput) -> float:
        rate = input_data.reduction_percent
        if rate is None:
            raise ValidationError("reduction_percent is required for spending_reduction")
        if rate <= 0 or rate >= 100:
            raise ValidationError("reduction_percent must be between 0 and 100 exclusive")
        return 1.0 - rate / 100.0

    @staticmethod
    def _supplier_consolidation_factor(input_data: ScenarioEngineInput) -> float:
        before = input_data.suppliers_before
        after = input_data.suppliers_after
        admin_rate = input_data.admin_savings_rate
        if before is None or after is None or admin_rate is None:
            raise ValidationError(
                "suppliers_before, suppliers_after, and admin_savings_rate "
                "are required for supplier_consolidation"
            )
        if before <= 0 or after <= 0 or after >= before:
            raise ValidationError(
                "suppliers_before must exceed suppliers_after and both must be positive"
            )
        reduction_share = (before - after) / before
        savings = reduction_share * (0.5 + admin_rate / 100.0)
        factor = 1.0 - savings
        if factor <= 0:
            raise BusinessRuleViolationError(
                "Supplier consolidation factor must remain positive"
            )
        return factor

    @staticmethod
    def _market_expansion_total(input_data: ScenarioEngineInput) -> float:
        growth = input_data.revenue_growth_percent
        cost = input_data.expansion_cost
        baseline = input_data.baseline.total_baseline
        if growth is None or cost is None:
            raise ValidationError(
                "revenue_growth_percent and expansion_cost are required "
                "for market_expansion"
            )
        if growth <= 0:
            raise ValidationError("revenue_growth_percent must be positive")
        if cost < 0:
            raise ValidationError("expansion_cost must not be negative")
        projected = baseline * (1.0 + growth / 100.0) - cost
        if projected <= 0:
            raise BusinessRuleViolationError(
                "Market expansion projected total must remain positive"
            )
        return projected

    @staticmethod
    def _category_outcomes(
        baseline: ScenarioBaselineInput,
        projected_factor: float,
        projected_total: float,
    ) -> tuple[ScenarioCategoryOutcome, ...]:
        if not baseline.categories:
            return ()
        baseline_sum = sum(item.amount for item in baseline.categories) or baseline.total_baseline
        outcomes: list[ScenarioCategoryOutcome] = []
        for item in sorted(baseline.categories, key=lambda c: c.category_name):
            base_amt = _money(item.amount)
            share = item.amount / baseline_sum if baseline_sum else 0.0
            proj_amt = _money(projected_total * share)
            change = _money(proj_amt - base_amt)
            direction = ScenarioCalculator._direction(change)
            outcomes.append(
                ScenarioCategoryOutcome(
                    category_name=item.category_name,
                    baseline_amount=base_amt,
                    projected_amount=proj_amt,
                    change_amount=change,
                    direction=direction,
                )
            )
        return tuple(outcomes)

    @staticmethod
    def _comparison_metrics(
        input_data: ScenarioEngineInput,
        baseline_total: float,
        projected_total: float,
        delta_percent: float,
    ) -> tuple[ScenarioComparisonOutcome, ...]:
        direction = ScenarioCalculator._direction(projected_total - baseline_total)
        change = ScenarioCalculator._format_percent(delta_percent)

        if input_data.archetype == ScenarioArchetype.SPENDING_REDUCTION:
            avg_before = baseline_total / max(len(input_data.baseline.categories), 1)
            avg_after = projected_total / max(len(input_data.baseline.categories), 1)
            return (
                ScenarioComparisonOutcome(
                    metric_name="إجمالي الإنفاق",
                    current_value=ScenarioCalculator._format_amount(baseline_total),
                    simulated_value=ScenarioCalculator._format_amount(projected_total),
                    change_value=change,
                    direction=direction,
                ),
                ScenarioComparisonOutcome(
                    metric_name="عدد الفئات",
                    current_value=str(len(input_data.baseline.categories)),
                    simulated_value=str(len(input_data.baseline.categories)),
                    change_value="0%",
                    direction=MetricDirection.NEUTRAL,
                ),
                ScenarioComparisonOutcome(
                    metric_name="متوسط الإنفاق للفئة",
                    current_value=ScenarioCalculator._format_amount(avg_before),
                    simulated_value=ScenarioCalculator._format_amount(avg_after),
                    change_value=change,
                    direction=direction,
                ),
            )

        if input_data.archetype == ScenarioArchetype.SUPPLIER_CONSOLIDATION:
            before = input_data.suppliers_before or 0
            after = input_data.suppliers_after or 0
            supplier_change = (
                _money(((after - before) / before) * 100) if before else 0.0
            )
            return (
                ScenarioComparisonOutcome(
                    metric_name="تكلفة الموردين",
                    current_value=ScenarioCalculator._format_amount(baseline_total),
                    simulated_value=ScenarioCalculator._format_amount(projected_total),
                    change_value=change,
                    direction=direction,
                ),
                ScenarioComparisonOutcome(
                    metric_name="عدد الموردين النشطين",
                    current_value=str(before),
                    simulated_value=str(after),
                    change_value=f"{supplier_change:+.1f}%",
                    direction=MetricDirection.DOWN if after < before else MetricDirection.NEUTRAL,
                ),
                ScenarioComparisonOutcome(
                    metric_name="تكلفة إدارية للموردين",
                    current_value=ScenarioCalculator._format_amount(baseline_total * 0.07),
                    simulated_value=ScenarioCalculator._format_amount(projected_total * 0.07),
                    change_value=change,
                    direction=direction,
                ),
            )

        cost = input_data.expansion_cost or 0.0
        growth = input_data.revenue_growth_percent or 0.0
        gross = baseline_total * (1.0 + growth / 100.0)
        margin_before = 18.2
        margin_after = _money((projected_total / gross) * 100) if gross else 0.0
        return (
            ScenarioComparisonOutcome(
                metric_name="إجمالي الإيرادات",
                current_value=ScenarioCalculator._format_amount(baseline_total),
                simulated_value=ScenarioCalculator._format_amount(gross),
                change_value=ScenarioCalculator._format_percent(growth),
                direction=MetricDirection.UP,
            ),
            ScenarioComparisonOutcome(
                metric_name="تكلفة التوسع",
                current_value="0",
                simulated_value=ScenarioCalculator._format_amount(cost),
                change_value=ScenarioCalculator._format_amount(cost),
                direction=MetricDirection.UP,
            ),
            ScenarioComparisonOutcome(
                metric_name="هامش الربح التشغيلي",
                current_value=f"{margin_before:.1f}%",
                simulated_value=f"{margin_after:.1f}%",
                change_value=f"{margin_after - margin_before:+.1f}%",
                direction=MetricDirection.DOWN if margin_after < margin_before else MetricDirection.UP,
            ),
        )

    @staticmethod
    def _chart_points(
        baseline_total: float,
        projected_total: float,
        horizon_quarters: int,
    ) -> tuple[ScenarioChartOutcome, ...]:
        labels = ("Q3 2026", "Q4 2026", "Q1 2027")
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
