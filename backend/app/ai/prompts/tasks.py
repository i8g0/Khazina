"""Prompt task identifiers."""

from __future__ import annotations

from enum import StrEnum


class PromptTask(StrEnum):
    EXECUTIVE_SUMMARY = "executive_summary"
    RISK_ANALYSIS = "risk_analysis"
    RECOMMENDATIONS = "recommendations"
    SCENARIO_ANALYSIS = "scenario_analysis"
