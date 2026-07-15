"""Shared fixtures for notification tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

from app.db.models.enums import AnalysisRunStatus, AnalysisType, ReportStatus, ReportType


def mock_active_user(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    *,
    is_active: bool = True,
) -> MagicMock:
    user = MagicMock()
    user.id = user_id
    user.organization_id = org_id
    user.is_active = is_active
    return user


def mock_waste_run(
    org_id: uuid.UUID,
    run_id: uuid.UUID,
    *,
    title: str = "Waste Q2",
    completed_at: datetime | None = None,
) -> MagicMock:
    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.analysis_type = AnalysisType.FINANCIAL_WASTE
    run.status = AnalysisRunStatus.COMPLETED
    run.title = title
    run.reporting_period_id = uuid.UUID("44444444-4444-4444-4444-444444444444")
    run.completed_at = completed_at or datetime(2026, 7, 15, 10, 0, tzinfo=UTC)
    run.runtime_metadata = {}
    return run


def mock_simulation_run(
    org_id: uuid.UUID,
    run_id: uuid.UUID,
    *,
    title: str = "Scenario Run",
) -> MagicMock:
    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.analysis_type = AnalysisType.SIMULATION
    run.status = AnalysisRunStatus.COMPLETED
    run.title = title
    run.reporting_period_id = uuid.UUID("44444444-4444-4444-4444-444444444444")
    run.completed_at = datetime(2026, 7, 15, 11, 0, tzinfo=UTC)
    run.runtime_metadata = {
        "scenario_provenance": {
            "scenario_id": str(uuid.uuid4()),
            "archetype": "cost_reduction",
        }
    }
    return run


def mock_simulation_result(*, result_title: str = "Cost Reduction") -> MagicMock:
    row = MagicMock()
    row.result_title = result_title
    row.result_description = "Projected savings"
    return row


def mock_report(
    org_id: uuid.UUID,
    report_id: uuid.UUID,
    *,
    status: str = ReportStatus.DRAFT,
    published_at: datetime | None = None,
) -> MagicMock:
    report = MagicMock()
    report.id = report_id
    report.organization_id = org_id
    report.title = "Executive Report"
    report.report_type = ReportType.ANALYSIS
    report.status = status
    report.reporting_period_id = uuid.UUID("44444444-4444-4444-4444-444444444444")
    report.published_at = published_at
    return report


def mock_period(*, label: str = "2026-Q2") -> MagicMock:
    period = MagicMock()
    period.label = label
    return period


def mock_resolved_settings(*, notifications_enabled: bool = True) -> MagicMock:
    prefs = MagicMock()
    prefs.notifications_enabled = notifications_enabled
    prefs.enabled_notification_kinds = frozenset(
        {
            "analysis_completed",
            "scenario_completed",
            "ai_recommendations_completed",
            "report_generated",
            "report_published",
        }
    )
    resolved = MagicMock()
    resolved.platform_default_notification_preferences = prefs
    return resolved
