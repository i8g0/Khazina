"""DecisionService orchestration unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.business.engines.waste import WasteEngine
from app.business.registry import freeze_registry, register_engine
from app.db.models.enums import AnalysisRunStatus, AnalysisType, ProcessingStatus
from app.decision.exceptions import SnapshotAdapterError
from app.decision.service import DecisionService
from tests.decision.conftest import sample_waste_payload


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def file_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def snapshot_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def run_id() -> uuid.UUID:
    return uuid.uuid4()


def _mock_file(org_id: uuid.UUID, file_id: uuid.UUID) -> MagicMock:
    file = MagicMock()
    file.id = file_id
    file.organization_id = org_id
    file.processing_status = ProcessingStatus.READY_FOR_ANALYSIS
    return file


def _mock_snapshot(
    org_id: uuid.UUID, file_id: uuid.UUID, snapshot_id: uuid.UUID
) -> MagicMock:
    snapshot = MagicMock()
    snapshot.id = snapshot_id
    snapshot.organization_id = org_id
    snapshot.financial_file_id = file_id
    snapshot.snapshot_version = 1
    snapshot.reporting_period_id = None
    snapshot.payload = sample_waste_payload()
    return snapshot


def _mock_run(
    org_id: uuid.UUID, run_id: uuid.UUID, file_id: uuid.UUID, snapshot_id: uuid.UUID
) -> MagicMock:
    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.source_file_id = file_id
    run.source_snapshot_id = snapshot_id
    run.analysis_type = AnalysisType.FINANCIAL_WASTE
    run.status = AnalysisRunStatus.PENDING
    run.runtime_metadata = {}
    run.reporting_period_id = None
    run.title = "Waste Q2"
    run.completed_at = datetime.now(UTC)
    return run


def test_execute_waste_analysis_success(
    org_id: uuid.UUID,
    file_id: uuid.UUID,
    snapshot_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    register_engine(WasteEngine())
    freeze_registry()

    session = MagicMock()
    analysis_service = MagicMock()
    waste_service = MagicMock()
    snapshot_repo = MagicMock()
    financial_repo = MagicMock()
    organization_repo = MagicMock()
    analysis_repo = MagicMock()

    financial_repo.get_file.return_value = _mock_file(org_id, file_id)
    snapshot_repo.get_latest_snapshot_for_file.return_value = _mock_snapshot(
        org_id, file_id, snapshot_id
    )

    pending_run = _mock_run(org_id, run_id, file_id, snapshot_id)
    completed_run = _mock_run(org_id, run_id, file_id, snapshot_id)
    completed_run.status = AnalysisRunStatus.COMPLETED

    analysis_service.create_run.return_value = pending_run
    analysis_service.start_run.return_value = pending_run
    analysis_service.complete_run.return_value = completed_run

    service = DecisionService(
        session,
        analysis_service,
        waste_service,
        snapshot_repo,
        financial_repo,
        organization_repo,
        analysis_repo,
    )

    outcome = service.execute_waste_analysis(
        org_id,
        title="Waste Q2",
        source_file_id=file_id,
    )

    assert outcome.analysis_run.status == AnalysisRunStatus.COMPLETED
    assert outcome.facts_contract.engine_id == "waste"
    waste_service.record_result.assert_called_once()
    analysis_service.complete_run.assert_called_once()
    call_kwargs = analysis_service.create_run.call_args.kwargs
    assert call_kwargs["source_snapshot_id"] == snapshot_id


def test_execute_waste_analysis_adapter_failure_fails_run(
    org_id: uuid.UUID,
    file_id: uuid.UUID,
    snapshot_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    register_engine(WasteEngine())
    freeze_registry()

    session = MagicMock()
    analysis_service = MagicMock()
    waste_service = MagicMock()
    snapshot_repo = MagicMock()
    financial_repo = MagicMock()
    organization_repo = MagicMock()
    analysis_repo = MagicMock()

    financial_repo.get_file.return_value = _mock_file(org_id, file_id)
    snapshot = _mock_snapshot(org_id, file_id, snapshot_id)
    snapshot.payload = {"source_file_name": "x", "sheets": []}
    snapshot_repo.get_latest_snapshot_for_file.return_value = snapshot

    pending_run = _mock_run(org_id, run_id, file_id, snapshot_id)
    analysis_service.create_run.return_value = pending_run
    analysis_service.start_run.return_value = pending_run

    adapter = MagicMock()
    adapter.adapt.side_effect = SnapshotAdapterError(
        "unsupported_layout", "No qualifying sheet"
    )

    service = DecisionService(
        session,
        analysis_service,
        waste_service,
        snapshot_repo,
        financial_repo,
        organization_repo,
        analysis_repo,
        waste_adapter=adapter,
    )

    with pytest.raises(SnapshotAdapterError):
        service.execute_waste_analysis(
            org_id,
            title="Waste Q2",
            source_file_id=file_id,
        )

    analysis_service.fail_run.assert_called_once()
    waste_service.record_result.assert_not_called()
