"""Scenario Engine input types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ScenarioArchetype(StrEnum):
    SPENDING_REDUCTION = "spending_reduction"
    SUPPLIER_CONSOLIDATION = "supplier_consolidation"
    MARKET_EXPANSION = "market_expansion"


@dataclass(frozen=True, slots=True)
class ScenarioCategoryBaseline:
    category_name: str
    amount: float


@dataclass(frozen=True, slots=True)
class ScenarioBaselineInput:
    total_baseline: float
    categories: tuple[ScenarioCategoryBaseline, ...]
    organization_id: str | None = None
    period: str | None = None
    source_dataset: str = "financial_snapshot_v1"
    generated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class ScenarioEngineInput:
    archetype: ScenarioArchetype
    baseline: ScenarioBaselineInput
    horizon_quarters: int = 3
    reduction_percent: float | None = None
    suppliers_before: int | None = None
    suppliers_after: int | None = None
    admin_savings_rate: float | None = None
    revenue_growth_percent: float | None = None
    expansion_cost: float | None = None
