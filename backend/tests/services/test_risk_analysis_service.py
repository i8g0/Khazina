"""RiskAnalysisService unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.business.bootstrap import initialize_business_engines
from app.business.engines.risk import RiskEngine
from app.db.models.enums import AnalysisRunStatus, AnalysisType
from app.decision.service import RiskDecisionExecutionOutcome
from app.services.exceptions import (
    DuplicateResourceError,
    InvalidStateError,
    ResourceNotFoundError,
)
from app.services.risk_analysis import RiskAnalysisService
from tests.business.risk_conftest import sample_risk_input


@pytest.fixture
def business_engines_initialized() -> None:
    initialize_business_engines()


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def run_id() -> uuid.UUID:
    return uuid.uuid4()


def test_execute_persists_gold_rows(
    business_engines_initialized: None,
    org_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    session = MagicMock()
    risk_repo = MagicMock()
    analysis_repo = MagicMock()
    org_repo = MagicMock()
    analysis_service = MagicMock()
    decision_service = MagicMock()

    snapshot = MagicMock()
    snapshot.id = uuid.uuid4()
    snapshot.snapshot_version = 1

    completed_run = MagicMock()
    completed_run.id = run_id
    completed_run.organization_id = org_id
    completed_run.analysis_type = AnalysisType.RISK
    completed_run.status = AnalysisRunStatus.COMPLETED

    engine_output = RiskEngine().run(sample_risk_input())
    decision_service.execute_risk_analysis.return_value = RiskDecisionExecutionOutcome(
        analysis_run=completed_run,
        engine_output=engine_output,
        snapshot=snapshot,
    )
    risk_repo.get_result_for_run.return_value = None
    risk_repo.create_result.side_effect = lambda result: result
    risk_repo.add_findings.side_effect = lambda rows: rows

    service = RiskAnalysisService(
        session,
        risk_repo,
        analysis_repo,
        org_repo,
        analysis_service,
        decision_service,
    )

    outcome = service.execute(
        org_id,
        title="Risk Q2",
        source_file_id=uuid.uuid4(),
    )

    assert outcome.result.total_findings == len(engine_output.findings)
    assert len(outcome.findings) == len(engine_output.findings)
    decision_service.execute_risk_analysis.assert_called_once()
    risk_repo.create_result.assert_called_once()
    risk_repo.add_findings.assert_called_once()
    session.commit.assert_called_once()


def test_execute_rejects_duplicate_result(
    business_engines_initialized: None,
    org_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    session = MagicMock()
    risk_repo = MagicMock()
    analysis_repo = MagicMock()
    org_repo = MagicMock()
    analysis_service = MagicMock()
    decision_service = MagicMock()

    snapshot = MagicMock()
    snapshot.id = uuid.uuid4()
    snapshot.snapshot_version = 1

    completed_run = MagicMock()
    completed_run.id = run_id

    engine_output = RiskEngine().run(sample_risk_input())
    decision_service.execute_risk_analysis.return_value = RiskDecisionExecutionOutcome(
        analysis_run=completed_run,
        engine_output=engine_output,
        snapshot=snapshot,
    )
    risk_repo.get_result_for_run.return_value = MagicMock()

    service = RiskAnalysisService(
        session,
        risk_repo,
        analysis_repo,
        org_repo,
        analysis_service,
        decision_service,
    )

    with pytest.raises(DuplicateResourceError):
        service.execute(
            org_id,
            title="Risk Q2",
            source_file_id=uuid.uuid4(),
        )

    risk_repo.create_result.assert_not_called()


def test_get_result_requires_risk_run_type(
    org_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    session = MagicMock()
    risk_repo = MagicMock()
    analysis_repo = MagicMock()
    org_repo = MagicMock()
    analysis_service = MagicMock()
    decision_service = MagicMock()

    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.analysis_type = AnalysisType.FINANCIAL_WASTE
    analysis_repo.get.return_value = run

    service = RiskAnalysisService(
        session,
        risk_repo,
        analysis_repo,
        org_repo,
        analysis_service,
        decision_service,
    )

    with pytest.raises(InvalidStateError):
        service.get_result(org_id, run_id)


def test_list_runs_delegates_to_analysis_service(org_id: uuid.UUID) -> None:
    session = MagicMock()
    risk_repo = MagicMock()
    analysis_repo = MagicMock()
    org_repo = MagicMock()
    analysis_service = MagicMock()
    decision_service = MagicMock()

    expected = [MagicMock()]
    analysis_service.list_runs.return_value = expected

    service = RiskAnalysisService(
        session,
        risk_repo,
        analysis_repo,
        org_repo,
        analysis_service,
        decision_service,
    )

    runs = service.list_runs(org_id, status="completed", limit=10, offset=0)
    assert runs == expected
    analysis_service.list_runs.assert_called_once_with(
        org_id,
        analysis_type=AnalysisType.RISK,
        status="completed",
        limit=10,
        offset=0,
    )


def test_get_finding_scoped_to_run(
    org_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    session = MagicMock()
    risk_repo = MagicMock()
    analysis_repo = MagicMock()
    org_repo = MagicMock()
    analysis_service = MagicMock()
    decision_service = MagicMock()

    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.analysis_type = AnalysisType.RISK
    analysis_repo.get.return_value = run

    finding_id = uuid.uuid4()
    finding = MagicMock()
    finding.id = finding_id
    finding.analysis_run_id = uuid.uuid4()
    finding.organization_id = org_id
    risk_repo.get_finding.return_value = finding

    service = RiskAnalysisService(
        session,
        risk_repo,
        analysis_repo,
        org_repo,
        analysis_service,
        decision_service,
    )

    with pytest.raises(ResourceNotFoundError):
        service.get_finding(org_id, run_id, finding_id)
