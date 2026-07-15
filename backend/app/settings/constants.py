"""Platform default configuration registry for Sprint 6.8 Settings."""

from __future__ import annotations

from app.db.models.enums import AnalysisType

DOCUMENT_VERSION = "1.0"

DEFAULT_LOCALE = "ar"
DEFAULT_DATE_DISPLAY_FORMAT = "gregorian"
DEFAULT_CURRENCY_DISPLAY_CODE = "SAR"

DEFAULT_ANALYSIS_TITLE_TEMPLATE = "{analysis_type} — {reporting_period_label}"
DEFAULT_REPORT_TITLE_TEMPLATE = "Executive Report — {analysis_type}"

DEFAULT_ENABLED_ANALYSIS_TYPES: frozenset[str] = frozenset(
    {
        AnalysisType.FINANCIAL_WASTE.value,
        AnalysisType.SIMULATION.value,
    }
)

NOTIFICATION_KIND_ANALYSIS_COMPLETED = "analysis_completed"
NOTIFICATION_KIND_SCENARIO_COMPLETED = "scenario_completed"
NOTIFICATION_KIND_AI_RECOMMENDATIONS_COMPLETED = "ai_recommendations_completed"
NOTIFICATION_KIND_REPORT_GENERATED = "report_generated"
NOTIFICATION_KIND_REPORT_PUBLISHED = "report_published"
NOTIFICATION_KIND_ANALYSIS_FAILED = "analysis_failed"
NOTIFICATION_KIND_SCENARIO_FAILED = "scenario_failed"

DEFAULT_ENABLED_NOTIFICATION_KINDS: frozenset[str] = frozenset(
    {
        NOTIFICATION_KIND_ANALYSIS_COMPLETED,
        NOTIFICATION_KIND_SCENARIO_COMPLETED,
        NOTIFICATION_KIND_AI_RECOMMENDATIONS_COMPLETED,
        NOTIFICATION_KIND_REPORT_GENERATED,
        NOTIFICATION_KIND_REPORT_PUBLISHED,
        NOTIFICATION_KIND_ANALYSIS_FAILED,
        NOTIFICATION_KIND_SCENARIO_FAILED,
    }
)

DEFAULT_PDF_EXPORT_ENABLED = True
DEFAULT_PDF_INCLUDE_COVER_PAGE = True
DEFAULT_PDF_INCLUDE_PROVENANCE_APPENDIX = True

FORBIDDEN_SETTINGS_KEYS: frozenset[str] = frozenset(
    {
        "ollama_model",
        "ollama_url",
        "ai_timeout",
        "thinking_enabled",
        "prompt_version",
    }
)

VALID_DATE_DISPLAY_FORMATS: frozenset[str] = frozenset({"gregorian", "hijri"})
