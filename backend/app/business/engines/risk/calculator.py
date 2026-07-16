"""Risk Calculator — deterministic financial metric derivation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from app.business.engines.risk.input import RiskEngineInput
from app.business.exceptions import ValidationError


def _money(value: Decimal | float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _percent(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True, slots=True)
class RiskCalculationResult:
    total_spend: Decimal
    total_waste_amount: Decimal
    waste_percentage: Decimal
    budget_total: Decimal | None
    actual_total: Decimal | None
    budget_variance_percentage: Decimal | None
    liquidity_ratio: Decimal | None
    top_category_name: str | None
    top_category_concentration: Decimal | None
    category_count: int
    organization_id: str
    snapshot_id: str
    reporting_period: str
    source_dataset: str
    generated_at: datetime | None = None


class RiskCalculator:
    """Derives normalized metrics used by category detectors. No classification."""

    def calculate(self, input_data: RiskEngineInput) -> RiskCalculationResult:
        metrics = input_data.financial_metrics
        total_spend = _money(metrics.total_spend)
        total_waste = _money(metrics.total_waste_amount)

        if total_spend <= 0:
            raise ValidationError("total_spend must be greater than zero")
        if total_waste < 0:
            raise ValidationError("total_waste_amount must not be negative")

        waste_pct = _percent((total_waste / total_spend) * Decimal("100"))

        budget_variance: Decimal | None = None
        if metrics.budget_total is not None and metrics.actual_total is not None:
            budget = _money(metrics.budget_total)
            actual = _money(metrics.actual_total)
            if budget > 0:
                budget_variance = _percent(((actual - budget) / budget) * Decimal("100"))

        liquidity_ratio: Decimal | None = None
        if (
            metrics.current_assets is not None
            and metrics.current_liabilities is not None
            and metrics.current_liabilities > 0
        ):
            liquidity_ratio = _percent(
                _money(metrics.current_assets) / _money(metrics.current_liabilities)
            )
        elif total_waste > 0:
            # W-1 proxy when balance-sheet fields absent: spend coverage of waste exposure
            liquidity_ratio = _percent(total_spend / total_waste)

        top_name: str | None = None
        top_concentration: Decimal | None = None
        if metrics.categories:
            top = max(metrics.categories, key=lambda row: row.share_of_waste)
            top_name = top.category_name
            top_concentration = top.share_of_waste

        return RiskCalculationResult(
            total_spend=total_spend,
            total_waste_amount=total_waste,
            waste_percentage=waste_pct,
            budget_total=(
                _money(metrics.budget_total) if metrics.budget_total is not None else None
            ),
            actual_total=(
                _money(metrics.actual_total) if metrics.actual_total is not None else None
            ),
            budget_variance_percentage=budget_variance,
            liquidity_ratio=liquidity_ratio,
            top_category_name=top_name,
            top_category_concentration=top_concentration,
            category_count=len(metrics.categories),
            organization_id=input_data.organization_id,
            snapshot_id=input_data.snapshot_id,
            reporting_period=input_data.reporting_period,
            source_dataset=input_data.source_dataset,
            generated_at=input_data.generated_at,
        )
