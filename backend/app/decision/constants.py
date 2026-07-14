"""Snapshot-to-Engine mapping aliases (§11 approved contract)."""

from __future__ import annotations

CATEGORY_ALIASES: frozenset[str] = frozenset(
    {
        "category",
        "waste_category",
        "category_name",
        "type",
        "فئة",
        "تصنيف",
        "التصنيف",
    }
)

WASTE_AMOUNT_ALIASES: frozenset[str] = frozenset(
    {
        "amount",
        "waste",
        "waste_amount",
        "detected_waste",
        "cost",
        "مبلغ",
        "مبلغ_الهدر",
        "الهدر",
    }
)

TOTAL_SPEND_FIXED_ALIASES: frozenset[str] = frozenset(
    {
        "total_spend",
        "spend",
        "total",
        "total_budget",
        "إجمالي",
        "إجمالي_الإنفاق",
        "الميزانية",
    }
)

BUDGET_SUM_ALIASES: frozenset[str] = frozenset({"budget"})

ACTUAL_SUM_ALIASES: frozenset[str] = frozenset({"actual"})

SOURCE_DATASET_FINANCIAL_SNAPSHOT_V1 = "financial_snapshot_v1"

SCHEMA_V1_REQUIRED_KEYS = frozenset({"source_file_name", "sheets"})
