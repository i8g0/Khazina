"""DecisionService risk analysis orchestration unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.business.bootstrap import initialize_business_engines
from app.db.models.enums import AnalysisRunStatus, AnalysisType, ProcessingStatus
from app.decision.service import DecisionService
from tests.decision.conftest import sample_waste_payload


@pytest.fixture
def business_engines_initialized() -> None:
    initialize_business_engines()


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


def test_execute_risk_analysis_success(
    business_engines_initialized: None,
    org_id: uuid.UUID,
    file_id: uuid.UUID,
    snapshot_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    session = MagicMock()
    analysis_service = MagicMock()
    waste_service = MagicMock()
    snapshot_repo = MagicMock()
    financial_repo = MagicMock()
    org_repo = MagicMock()
    analysis_repo = MagicMock()

    source_file = _mock_file(org_id, file_id)
    snapshot = _mock_snapshot(org_id, file_id, snapshot_id)
    pending_run = MagicMock()
    pending_run.id = run_id
    pending_run.organization_id = org_id
    pending_run.source_file_id = file_id
    pending_run.source_snapshot_id = snapshot_id
    pending_run.analysis_type = AnalysisType.RISK
    pending_run.status = AnalysisRunStatus.PENDING
    pending_run.runtime_metadata = {}
    pending_run.reporting_period_id = None
    pending_run.title = "Risk Q2"
    pending_run.completed_at = datetime.now(UTC)

    completed_run = MagicMock()
    completed_run.id = run_id
    completed_run.status = AnalysisRunStatus.COMPLETED
    completed_run.runtime_metadata = {
        "facts_contract": {},
        "risk_findings": [],
    }

    financial_repo.get_file.return_value = source_file
    snapshot_repo.get_latest_snapshot_for_file.return_value = snapshot
    analysis_service.create_run.return_value = pending_run
    analysis_service.complete_run.return_value = completed_run

    service = DecisionService(
        session,
        analysis_service,
        waste_service,
        snapshot_repo,
        financial_repo,
        org_repo,
        analysis_repo,
    )

    outcome = service.execute_risk_analysis(
        org_id,
        title="Risk Q2",
        source_file_id=file_id,
    )

    assert outcome.analysis_run.status == AnalysisRunStatus.COMPLETED
    assert outcome.engine_output.facts_contract.engine_id == "risk"
    assert len(outcome.engine_output.findings) >= 1
    analysis_service.create_run.assert_called_once()
    call_kwargs = analysis_service.create_run.call_args.kwargs
    assert call_kwargs["analysis_type"] == AnalysisType.RISK
    complete_kwargs = analysis_service.complete_run.call_args.kwargs
    assert "facts_contract" in complete_kwargs["success_metadata"]
    assert "risk_findings" in complete_kwargs["success_metadata"]
    assert "promoted" not in str(complete_kwargs["success_metadata"]).lower()
