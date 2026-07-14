"""Scenario adapter constants (S-1 layout)."""

from __future__ import annotations

from app.decision.constants import (
    ACTUAL_SUM_ALIASES,
    BUDGET_SUM_ALIASES,
    SCHEMA_V1_REQUIRED_KEYS,
    SOURCE_DATASET_FINANCIAL_SNAPSHOT_V1,
    TOTAL_SPEND_FIXED_ALIASES,
)

SCENARIO_CATEGORY_ALIASES: frozenset[str] = frozenset(
    {
        "category",
        "category_name",
        "department",
        "department_name",
        "dept",
        "type",
        "فئة",
        "تصنيف",
        "التصنيف",
        "قسم",
        "الإدارة",
    }
)

SCENARIO_AMOUNT_ALIASES: frozenset[str] = frozenset(
    {
        "amount",
        "spend",
        "cost",
        "budget",
        "actual",
        "revenue",
        "إنفاق",
        "مبلغ",
        "إيراد",
    }
)

BASELINE_MISMATCH_TOLERANCE = 0.05

DEFAULT_HORIZON_QUARTERS = 3

__all__ = [
    "ACTUAL_SUM_ALIASES",
    "BASELINE_MISMATCH_TOLERANCE",
    "BUDGET_SUM_ALIASES",
    "DEFAULT_HORIZON_QUARTERS",
    "SCENARIO_AMOUNT_ALIASES",
    "SCENARIO_CATEGORY_ALIASES",
    "SCHEMA_V1_REQUIRED_KEYS",
    "SOURCE_DATASET_FINANCIAL_SNAPSHOT_V1",
    "TOTAL_SPEND_FIXED_ALIASES",
]
