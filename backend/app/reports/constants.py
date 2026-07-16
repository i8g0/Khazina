"""Report Builder constants."""

from __future__ import annotations

BUILDER_VERSION = "1.0.0"
REPORT_DOCUMENT_VERSION = "1.0"
PDF_RENDERER_VERSION = "2.1"
EXPORT_FORMAT_PDF = "pdf"

PROFILE_WASTE_DECISION = "waste_decision"
PROFILE_SCENARIO = "scenario"
PROFILE_RISK = "risk"

WASTE_SECTION_ORDER: tuple[str, ...] = (
    "cover",
    "executive_summary",
    "decision_highlights",
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

RISK_SECTION_ORDER: tuple[str, ...] = (
    "cover",
    "executive_summary",
    "risk_summary",
    "top_risks",
    "mitigation_status",
    "register_statistics",
    "recommendations",
    "provenance",
)

SUPPORTED_ANALYSIS_TYPES: frozenset[str] = frozenset(
    {"financial_waste", "simulation", "risk"}
)

ANALYSIS_TYPE_TO_REPORT_TYPE: dict[str, str] = {
    "financial_waste": "analysis",
    "simulation": "simulation",
    "risk": "risk",
}

ANALYSIS_TYPE_TO_PROFILE: dict[str, str] = {
    "financial_waste": PROFILE_WASTE_DECISION,
    "simulation": PROFILE_SCENARIO,
    "risk": PROFILE_RISK,
}

SUPPORTED_ENGINE_IDS: frozenset[str] = frozenset({"waste", "scenario", "risk"})
