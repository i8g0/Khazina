"""Platform Event kinds and notification constants (Sprint 6.7)."""

from __future__ import annotations

NOTIFICATION_VERSION = "1.0"

KIND_ANALYSIS_COMPLETED = "analysis_completed"
KIND_SCENARIO_COMPLETED = "scenario_completed"
KIND_AI_RECOMMENDATIONS_COMPLETED = "ai_recommendations_completed"
KIND_REPORT_GENERATED = "report_generated"
KIND_REPORT_PUBLISHED = "report_published"

ALL_PLATFORM_EVENT_KINDS: frozenset[str] = frozenset(
    {
        KIND_ANALYSIS_COMPLETED,
        KIND_SCENARIO_COMPLETED,
        KIND_AI_RECOMMENDATIONS_COMPLETED,
        KIND_REPORT_GENERATED,
        KIND_REPORT_PUBLISHED,
    }
)

STATUS_ACTIVE = "active"
