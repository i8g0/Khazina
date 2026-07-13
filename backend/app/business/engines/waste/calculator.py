"""Waste Calculator — deterministic financial calculations only."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from app.business.engines.waste.input import WasteEngineInput
from app.business.exceptions import ValidationError


def _money(value: float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _percent(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True, slots=True)
class WasteCategoryCalculation:
    category_name: str
    amount: Decimal
    percentage_of_waste: Decimal


@dataclass(frozen=True, slots=True)
class WasteCalculationResult:
    total_spend: Decimal
    total_waste_amount: Decimal
    waste_percentage: Decimal
    categories: tuple[WasteCategoryCalculation, ...]
    top_category_name: str | None
    top_category_percentage: Decimal | None
    recoverable_savings_rate: Decimal
    potential_savings_amount: Decimal
    active_savings_opportunities: int
    organization_id: str | None = None
    period: str | None = None
    source_dataset: str = "waste_analysis"
    generated_at: datetime | None = None


class WasteCalculator:
    """Performs deterministic waste financial calculations. No interpretation."""

    RECOVERABLE_SAVINGS_RATE = Decimal("0.80")
    SAVINGS_OPPORTUNITY_THRESHOLD = Decimal("15.00")

    def calculate(self, input_data: WasteEngineInput) -> WasteCalculationResult:
        total_spend = _money(input_data.total_spend)
        total_waste = _money(input_data.total_waste_amount)

        if total_spend <= 0:
            raise ValidationError("total_spend must be greater than zero")

        waste_percentage = _percent((total_waste / total_spend) * Decimal("100"))

        category_rows: list[WasteCategoryCalculation] = []
        for category in input_data.categories:
            amount = _money(category.amount)
            if total_waste > 0:
                share = _percent((amount / total_waste) * Decimal("100"))
            else:
                share = Decimal("0.00")
            category_rows.append(
                WasteCategoryCalculation(
                    category_name=category.category_name,
                    amount=amount,
                    percentage_of_waste=share,
                )
            )

        top_name: str | None = None
        top_share: Decimal | None = None
        if category_rows:
            top = max(category_rows, key=lambda row: row.amount)
            top_name = top.category_name
            top_share = top.percentage_of_waste

        potential_savings = _money(total_waste * self.RECOVERABLE_SAVINGS_RATE)
        opportunities = sum(
            1
            for row in category_rows
            if row.percentage_of_waste >= self.SAVINGS_OPPORTUNITY_THRESHOLD
        )

        return WasteCalculationResult(
            total_spend=total_spend,
            total_waste_amount=total_waste,
            waste_percentage=waste_percentage,
            categories=tuple(category_rows),
            top_category_name=top_name,
            top_category_percentage=top_share,
            recoverable_savings_rate=self.RECOVERABLE_SAVINGS_RATE,
            potential_savings_amount=potential_savings,
            active_savings_opportunities=opportunities,
            organization_id=input_data.organization_id,
            period=input_data.period,
            source_dataset=input_data.source_dataset,
            generated_at=input_data.generated_at,
        )
