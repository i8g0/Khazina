"""Waste Engine input types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class WasteCategoryInput:
    """Waste amount attributed to a single category."""

    category_name: str
    amount: float


@dataclass(frozen=True, slots=True)
class WasteEngineInput:
    """Validated input for the Waste Engine lifecycle."""

    total_spend: float
    total_waste_amount: float
    categories: tuple[WasteCategoryInput, ...]
    organization_id: str | None = None
    period: str | None = None
    source_dataset: str = "waste_analysis"
    generated_at: datetime | None = None
