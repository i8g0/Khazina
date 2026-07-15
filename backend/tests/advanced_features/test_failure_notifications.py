"""Failure notification builder tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from app.db.models.enums import AnalysisRunStatus, AnalysisType, RelatedEntityType
from app.notifications.builder import NotificationBuilder
from app.notifications.constants import KIND_ANALYSIS_FAILED, KIND_SCENARIO_FAILED


def _builder() -> tuple[NotificationBuilder, dict[str, MagicMock]]:
    session = MagicMock()
    repos = {
        "notifications": MagicMock(),
        "analyses": MagicMock(),
        "reports": MagicMock(),
        "recommendations": MagicMock(),
        "simulations": MagicMock(),
        "organizations": MagicMock(),
        "users": MagicMock(),
        "user_preferences": MagicMock(),
    }
    repos["notifications"].get_by_fingerprint.return_value = None
    repos["notifications"].create.side_effect = lambda n: n
    repos["user_preferences"].get_by_user.return_value = None
    session.commit = MagicMock()
    session.rollback = MagicMock()
    builder = NotificationBuilder(
        session,
        repos["notifications"],
        repos["analyses"],
        repos["reports"],
        repos["recommendations"],
        repos["simulations"],
        repos["organizations"],
        repos["users"],
        settings_service=None,
        user_preferences_repository=repos["user_preferences"],
    )
    return builder, repos


def test_waste_failure_materializes_analysis_failed() -> None:
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    run_id = uuid.uuid4()
    builder, repos = _builder()
    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.analysis_type = AnalysisType.FINANCIAL_WASTE
    run.title = "Waste Q2"
    run.reporting_period_id = None
    run.completed_at = datetime(2026, 7, 15, tzinfo=UTC)
    run.runtime_metadata = {"failure": {"error_code": "adapter_error"}}
    repos["analyses"].get.return_value = run
    user = MagicMock()
    user.id = user_id
    user.organization_id = org_id
    user.is_active = True
    repos["users"].get_by_id.return_value = user

    result = builder.materialize_analysis_failure(
        org_id, run_id, initiating_user_id=user_id
    )

    assert result is not None
    assert result.created is True
    assert result.notification.platform_event_kind == KIND_ANALYSIS_FAILED


def test_simulation_failure_uses_scenario_failed_kind() -> None:
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    run_id = uuid.uuid4()
    builder, repos = _builder()
    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.analysis_type = AnalysisType.SIMULATION
    run.title = "Scenario"
    run.reporting_period_id = None
    run.completed_at = datetime(2026, 7, 15, tzinfo=UTC)
    run.runtime_metadata = {"failure": {"error_code": "engine_execution_failed"}}
    repos["analyses"].get.return_value = run
    user = MagicMock()
    user.id = user_id
    user.organization_id = org_id
    user.is_active = True
    repos["users"].get_by_id.return_value = user

    result = builder.materialize_analysis_failure(
        org_id, run_id, initiating_user_id=user_id
    )

    assert result is not None
    assert result.notification.platform_event_kind == KIND_SCENARIO_FAILED
    assert result.notification.platform_event_kind != KIND_ANALYSIS_FAILED


def test_missing_initiating_user_skips_failure_notification() -> None:
    builder, repos = _builder()
    result = builder.materialize_analysis_failure(
        uuid.uuid4(), uuid.uuid4(), initiating_user_id=None
    )
    assert result is None
    repos["notifications"].create.assert_not_called()
