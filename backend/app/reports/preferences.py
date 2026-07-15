"""Report assembly preference inputs from organization settings."""

from __future__ import annotations

from dataclasses import dataclass

from app.settings.constants import (
    DEFAULT_CURRENCY_DISPLAY_CODE,
    DEFAULT_DATE_DISPLAY_FORMAT,
)


@dataclass(frozen=True, slots=True)
class ReportAssemblyPreferences:
    include_ai_sections_when_available: bool = True
    include_recommendations_section: bool = True
    include_scenario_provenance_section: bool = True
    report_language: str = "ar"
    date_display_format: str = DEFAULT_DATE_DISPLAY_FORMAT
    currency_display_code: str = DEFAULT_CURRENCY_DISPLAY_CODE
    default_report_title_template: str = "Executive Report — {analysis_type}"
    require_ai_insights_before_report: bool = False
