"""Risk category taxonomy — Sprint 9.2 (Phase 9 architecture §3.1)."""

from __future__ import annotations

from dataclasses import dataclass

CATEGORY_FINANCIAL = "financial"
CATEGORY_LIQUIDITY = "liquidity"
CATEGORY_OPERATIONAL = "operational"
CATEGORY_COMPLIANCE = "compliance"
CATEGORY_VENDOR = "vendor"
CATEGORY_FRAUD = "fraud"
CATEGORY_STRATEGIC = "strategic"
CATEGORY_BUDGET = "budget"
CATEGORY_FORECAST = "forecast"

ALL_CATEGORY_CODES: frozenset[str] = frozenset(
    {
        CATEGORY_FINANCIAL,
        CATEGORY_LIQUIDITY,
        CATEGORY_OPERATIONAL,
        CATEGORY_COMPLIANCE,
        CATEGORY_VENDOR,
        CATEGORY_FRAUD,
        CATEGORY_STRATEGIC,
        CATEGORY_BUDGET,
        CATEGORY_FORECAST,
    }
)

POSTURE_ELEVATED = "elevated"
POSTURE_MODERATE = "moderate"
POSTURE_LOW = "low"

FINDING_STATUS_DETECTED = "detected"


@dataclass(frozen=True, slots=True)
class RiskCategoryDefinition:
    code: str
    label_en: str
    label_ar: str
    sort_order: int


RISK_CATEGORIES: tuple[RiskCategoryDefinition, ...] = (
    RiskCategoryDefinition(CATEGORY_FINANCIAL, "Financial", "مخاطر مالية", 1),
    RiskCategoryDefinition(CATEGORY_LIQUIDITY, "Liquidity", "مخاطر السيولة", 2),
    RiskCategoryDefinition(CATEGORY_OPERATIONAL, "Operational", "مخاطر تشغيلية", 3),
    RiskCategoryDefinition(CATEGORY_COMPLIANCE, "Compliance", "مخاطر امتثال", 4),
    RiskCategoryDefinition(CATEGORY_VENDOR, "Vendor", "مخاطر الموردين", 5),
    RiskCategoryDefinition(CATEGORY_FRAUD, "Fraud", "مخاطر احتيال", 6),
    RiskCategoryDefinition(CATEGORY_STRATEGIC, "Strategic", "مخاطر استراتيجية", 7),
    RiskCategoryDefinition(CATEGORY_BUDGET, "Budget", "مخاطر الموازنة", 8),
    RiskCategoryDefinition(CATEGORY_FORECAST, "Forecast", "مخاطر التوقعات", 9),
)
