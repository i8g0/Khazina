"""Prompt task identifiers."""

from __future__ import annotations

from enum import StrEnum


class PromptTask(StrEnum):
    EXECUTIVE_SUMMARY = "executive_summary"
    RISK_ANALYSIS = "risk_analysis"
    RECOMMENDATIONS = "recommendations"
    SCENARIO_ANALYSIS = "scenario_analysis"
    RISK_EXECUTIVE_SUMMARY = "risk_executive_summary"
    RISK_EXECUTIVE_BRIEF = "risk_executive_brief"
    RISK_EXPLANATION = "risk_explanation"
    RISK_MITIGATION_OPTIONS = "risk_mitigation_options"
    RISK_BOARD_REPORT = "risk_board_report"
