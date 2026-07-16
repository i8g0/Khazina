"""Backward-compatible re-exports — use business_labels for new code."""

from __future__ import annotations

from app.presentation.business_labels import (
    CATEGORY_LABELS_AR as WASTE_CATEGORY_LABELS_AR,
    category_label_ar as waste_category_label_ar,
    department_hint_ar as waste_category_owner_hint,
)

__all__ = [
    "WASTE_CATEGORY_LABELS_AR",
    "waste_category_label_ar",
    "waste_category_owner_hint",
]
