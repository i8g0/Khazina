"""Report Builder constants."""

from __future__ import annotations

BUILDER_VERSION = "1.0.0"
REPORT_DOCUMENT_VERSION = "1.0"

PROFILE_WASTE_DECISION = "waste_decision"
PROFILE_SCENARIO = "scenario"

WASTE_SECTION_ORDER: tuple[str, ...] = (
    "cover",
    "executive_summary",
    "key_metrics",
    "waste_analysis",
    "risk_explanation",
    "recommendations",
    "provenance",
)

SCENARIO_SECTION_ORDER: tuple[str, ...] = (
    "cover",
    "executive_summary",
    "scenario_overview",
    "forecast_and_delta",
    "impact_and_actions",
    "key_metrics",
    "baseline_context",
    "provenance",
)

SUPPORTED_ANALYSIS_TYPES: frozenset[str] = frozenset({"financial_waste", "simulation"})

ANALYSIS_TYPE_TO_REPORT_TYPE: dict[str, str] = {
    "financial_waste": "analysis",
    "simulation": "simulation",
}

ANALYSIS_TYPE_TO_PROFILE: dict[str, str] = {
    "financial_waste": PROFILE_WASTE_DECISION,
    "simulation": PROFILE_SCENARIO,
}

SUPPORTED_ENGINE_IDS: frozenset[str] = frozenset({"waste", "scenario"})
