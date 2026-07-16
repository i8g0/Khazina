"""NotificationBuilder materialization tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.db.models.enums import AnalysisType, RelatedEntityType, ReportStatus
from app.db.models.notification import Notification
from app.notifications.builder import NotificationBuilder
from app.notifications.constants import (
    KIND_AI_RECOMMENDATIONS_COMPLETED,
    KIND_ANALYSIS_COMPLETED,
    KIND_RISK_ANALYSIS_COMPLETED,
    KIND_REPORT_GENERATED,
    KIND_REPORT_PUBLISHED,
    KIND_SCENARIO_COMPLETED,
)
from app.settings.service import SettingsService
from tests.notifications.conftest import (
    mock_active_user,
    mock_period,
    mock_report,
    mock_resolved_settings,
    mock_simulation_result,
    mock_simulation_run,
    mock_waste_run,
)


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


def _builder(
    *,
    settings_service: SettingsService | None = None,
) -> tuple[NotificationBuilder, dict[str, MagicMock]]:
    session = MagicMock()
    repos = {
        "notifications": MagicMock(),
        "analyses": MagicMock(),
        "reports": MagicMock(),
        "recommendations": MagicMock(),
        "simulations": MagicMock(),
        "organizations": MagicMock(),
        "users": MagicMock(),
    }
    repos["notifications"].get_by_fingerprint.return_value = None
    repos["notifications"].create.side_effect = lambda n: n
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
        settings_service=settings_service,
    )
    return builder, repos


def test_waste_analysis_completion_materializes(
    org_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    run_id = uuid.uuid4()
    builder, repos = _builder()
    repos["analyses"].get.return_value = mock_waste_run(org_id, run_id)
    repos["users"].get_by_id.return_value = mock_active_user(org_id, user_id)
    repos["organizations"].get_reporting_period.return_value = mock_period()

    result = builder.materialize_analysis_completion(
        org_id, run_id, initiating_user_id=user_id
    )

    assert result is not None
    assert result.created is True
    assert result.notification.platform_event_kind == KIND_ANALYSIS_COMPLETED
    assert result.notification.recipient_user_id == user_id
    assert result.notification.source_entity_type == RelatedEntityType.ANALYSIS_RUN
    assert result.notification.source_entity_id == run_id


def test_simulation_completion_uses_scenario_kind(
    org_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    run_id = uuid.uuid4()
    builder, repos = _builder()
    run = mock_simulation_run(org_id, run_id)
    repos["analyses"].get.return_value = run
    repos["simulations"].get_run_for_analysis_run.return_value = mock_simulation_result()
    repos["users"].get_by_id.return_value = mock_active_user(org_id, user_id)
    repos["organizations"].get_reporting_period.return_value = mock_period()

    result = builder.materialize_analysis_completion(
        org_id, run_id, initiating_user_id=user_id
    )

    assert result is not None
    assert result.notification.platform_event_kind == KIND_SCENARIO_COMPLETED
    assert result.notification.platform_event_kind != KIND_ANALYSIS_COMPLETED


def test_ai_recommendations_completion_materializes(
    org_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    run_id = uuid.uuid4()
    builder, repos = _builder()
    run = mock_waste_run(org_id, run_id)
    run.runtime_metadata = {
        "ai_insights": {
            "generated_at": "2026-07-15T10:00:00+00:00",
            "model": "qwen3.5:2b",
            "prompt_version": "1.0",
        }
    }
    repos["analyses"].get.return_value = run
    repos["users"].get_by_id.return_value = mock_active_user(org_id, user_id)

    result = builder.materialize_ai_recommendations_completion(
        org_id,
        run_id,
        initiating_user_id=user_id,
        recommendation_count=2,
    )

    assert result is not None
    assert result.notification.platform_event_kind == KIND_AI_RECOMMENDATIONS_COMPLETED


def test_risk_analysis_completion_materializes(
    org_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    run_id = uuid.uuid4()
    builder, repos = _builder()
    run = mock_waste_run(org_id, run_id)
    run.analysis_type = AnalysisType.RISK
    repos["analyses"].get.return_value = run
    repos["organizations"].get_reporting_period.return_value = mock_period()
    repos["users"].get_by_id.return_value = mock_active_user(org_id, user_id)

    result = builder.materialize_analysis_completion(
        org_id,
        run_id,
        initiating_user_id=user_id,
    )

    assert result is not None
    assert result.notification.platform_event_kind == KIND_RISK_ANALYSIS_COMPLETED


def test_report_generated_materializes(org_id: uuid.UUID, user_id: uuid.UUID) -> None:
    report_id = uuid.uuid4()
    builder, repos = _builder()
    repos["reports"].get.return_value = mock_report(org_id, report_id)
    repos["users"].get_by_id.return_value = mock_active_user(org_id, user_id)

    result = builder.materialize_report_generated(
        org_id, report_id, initiating_user_id=user_id
    )

    assert result is not None
    assert result.notification.platform_event_kind == KIND_REPORT_GENERATED
    assert result.notification.source_entity_type == RelatedEntityType.REPORT


def test_report_published_materializes(org_id: uuid.UUID, user_id: uuid.UUID) -> None:
    report_id = uuid.uuid4()
    builder, repos = _builder()
    repos["reports"].get.return_value = mock_report(
        org_id,
        report_id,
        status=ReportStatus.READY,
        published_at=datetime(2026, 7, 15, 12, 0, tzinfo=UTC),
    )
    repos["users"].get_by_id.return_value = mock_active_user(org_id, user_id)

    result = builder.materialize_report_published(
        org_id, report_id, initiating_user_id=user_id
    )

    assert result is not None
    assert result.notification.platform_event_kind == KIND_REPORT_PUBLISHED


def test_missing_initiating_user_skips_materialization(
    org_id: uuid.UUID,
) -> None:
    builder, repos = _builder()
    result = builder.materialize_analysis_completion(
        org_id, uuid.uuid4(), initiating_user_id=None
    )
    assert result is None
    repos["notifications"].create.assert_not_called()


def test_duplicate_fingerprint_is_idempotent(
    org_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    run_id = uuid.uuid4()
    builder, repos = _builder()
    repos["analyses"].get.return_value = mock_waste_run(org_id, run_id)
    repos["users"].get_by_id.return_value = mock_active_user(org_id, user_id)
    existing = Notification(
        organization_id=org_id,
        recipient_user_id=user_id,
        platform_event_kind=KIND_ANALYSIS_COMPLETED,
        title="existing",
        body="existing",
        source_entity_type=RelatedEntityType.ANALYSIS_RUN,
        source_entity_id=run_id,
        reporting_period_id=None,
        event_fingerprint="abc",
        payload_representation={},
        materialized_at=datetime.now(UTC),
        status="active",
    )
    repos["notifications"].get_by_fingerprint.return_value = existing

    result = builder.materialize_analysis_completion(
        org_id, run_id, initiating_user_id=user_id
    )

    assert result is not None
    assert result.created is False
    assert result.notification is existing
    repos["notifications"].create.assert_not_called()


def test_settings_gate_disables_materialization(
    org_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    settings = MagicMock(spec=SettingsService)
    settings.get_resolved_settings.return_value = mock_resolved_settings(
        notifications_enabled=False
    )
    builder, repos = _builder(settings_service=settings)
    repos["analyses"].get.return_value = mock_waste_run(org_id, uuid.uuid4())

    result = builder.materialize_analysis_completion(
        org_id, uuid.uuid4(), initiating_user_id=user_id
    )

    assert result is None
    repos["notifications"].create.assert_not_called()


def test_inactive_recipient_skips_materialization(
    org_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    run_id = uuid.uuid4()
    builder, repos = _builder()
    repos["analyses"].get.return_value = mock_waste_run(org_id, run_id)
    repos["users"].get_by_id.return_value = mock_active_user(
        org_id, user_id, is_active=False
    )

    result = builder.materialize_analysis_completion(
        org_id, run_id, initiating_user_id=user_id
    )

    assert result is None
    repos["notifications"].create.assert_not_called()
