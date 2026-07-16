"""Shared fixtures for risk engine tests."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.business.engines.risk.input import (
    FinancialMetricsInput,
    RiskEngineInput,
    WasteCategoryMetric,
)


def sample_risk_input(*, waste_percentage: Decimal | None = None) -> RiskEngineInput:
    total_spend = Decimal("50000000.00")
    total_waste = Decimal("2340000.00")
    if waste_percentage is not None:
        total_waste = (total_spend * waste_percentage / Decimal("100")).quantize(
            Decimal("0.01")
        )

    categories = (
        WasteCategoryMetric("finance", Decimal("1075000.00"), Decimal("45.94")),
        WasteCategoryMetric("overlapping_contracts", Decimal("745000.00"), Decimal("31.84")),
        WasteCategoryMetric("operations", Decimal("520000.00"), Decimal("22.22")),
    )
    # normalize shares if custom waste amount
    if waste_percentage is not None:
        categories = tuple(
            WasteCategoryMetric(
                row.category_name,
                row.amount,
                (row.amount / total_waste * Decimal("100")).quantize(Decimal("0.01")),
            )
            for row in categories
        )

    return RiskEngineInput(
        organization_id="org-123",
        snapshot_id="snap-456",
        reporting_period="2026-Q2",
        financial_metrics=FinancialMetricsInput(
            total_spend=total_spend,
            total_waste_amount=total_waste,
            waste_percentage=(total_waste / total_spend * Decimal("100")).quantize(
                Decimal("0.01")
            ),
            categories=categories,
        ),
        generated_at=datetime(2026, 7, 16, tzinfo=UTC),
    )
