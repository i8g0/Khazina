"""Risk Engine input types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True)
class WasteCategoryMetric:
    category_name: str
    amount: Decimal
    share_of_waste: Decimal


@dataclass(frozen=True, slots=True)
class FinancialMetricsInput:
    """Normalized financial metrics derived from snapshot Silver payload."""

    total_spend: Decimal
    total_waste_amount: Decimal
    waste_percentage: Decimal
    budget_total: Decimal | None = None
    actual_total: Decimal | None = None
    current_assets: Decimal | None = None
    current_liabilities: Decimal | None = None
    categories: tuple[WasteCategoryMetric, ...] = ()


@dataclass(frozen=True, slots=True)
class WasteFactsReference:
    """Optional read-only waste Facts Contract summary for cross-domain rules."""

    waste_percentage: Decimal | None = None
    overall_level: str | None = None
    top_category: str | None = None


@dataclass(frozen=True, slots=True)
class SimulationSummaryReference:
    """Optional read-only simulation output for strategic/forecast rules."""

    baseline_metric: Decimal | None = None
    projected_metric: Decimal | None = None
    variance_percentage: Decimal | None = None


@dataclass(frozen=True, slots=True)
class RiskRuleProfile:
    """Org-configurable thresholds; defaults applied when absent."""

    enabled_categories: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "financial",
                "liquidity",
                "operational",
                "compliance",
                "vendor",
                "fraud",
                "budget",
            }
        )
    )


@dataclass(frozen=True, slots=True)
class RiskEngineInput:
    """Validated input for the Risk Engine lifecycle."""

    organization_id: str
    snapshot_id: str
    reporting_period: str
    financial_metrics: FinancialMetricsInput
    waste_facts: WasteFactsReference | None = None
    simulation_summary: SimulationSummaryReference | None = None
    existing_register_summary: dict[str, int] | None = None
    rule_profile: RiskRuleProfile = RiskRuleProfile()
    source_dataset: str = "financial_snapshot_v1"
    generated_at: datetime | None = None

    def enabled_categories(self) -> frozenset[str]:
        return self.rule_profile.enabled_categories
