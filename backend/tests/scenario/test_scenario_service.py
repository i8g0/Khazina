"""ScenarioService orchestration tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.business.bootstrap import initialize_business_engines
from app.db.models.enums import AnalysisRunStatus, AnalysisType, ProcessingStatus
from app.scenario.service import ScenarioService
from app.services.exceptions import InvalidStateError
from tests.scenario.conftest import sample_scenario_snapshot_payload


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def scenario_id() -> uuid.UUID:
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


def _mock_scenario(org_id: uuid.UUID, scenario_id: uuid.UUID) -> MagicMock:
    scenario = MagicMock()
    scenario.id = scenario_id
    scenario.organization_id = org_id
    scenario.name = "تقليل الإنفاق 10%"
    scenario.description = "محاكاة خفض الإنفاق"
    scenario.status = "draft"
    return scenario


def _mock_assumptions() -> list[MagicMock]:
    rows = []
    for label, value in (
        ("نسبة خفض الإنفاق", "10%"),
        ("الأفق الزمني", "3 أرباع"),
    ):
        row = MagicMock()
        row.label = label
        row.value = value
        rows.append(row)
    return rows


def test_execute_scenario_success(
    org_id: uuid.UUID,
    scenario_id: uuid.UUID,
    file_id: uuid.UUID,
    snapshot_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    initialize_business_engines()
    session = MagicMock()
    analysis_service = MagicMock()
    analysis_repo = MagicMock()
    simulation_repo = MagicMock()
    snapshot_repo = MagicMock()
    financial_repo = MagicMock()
    organization_repo = MagicMock()
    waste_repo = MagicMock()

    scenario = _mock_scenario(org_id, scenario_id)
    simulation_repo.get_scenario.return_value = scenario
    simulation_repo.list_assumptions.return_value = _mock_assumptions()
    simulation_repo.create_run.side_effect = lambda run: run
    simulation_repo.require_run.side_effect = lambda rid: MagicMock(id=rid)
    simulation_repo.get_run.return_value = MagicMock(id=uuid.uuid4())

    file = MagicMock()
    file.id = file_id
    file.organization_id = org_id
    file.processing_status = ProcessingStatus.READY_FOR_ANALYSIS
    financial_repo.get_file.return_value = file

    snapshot = MagicMock()
    snapshot.id = snapshot_id
    snapshot.organization_id = org_id
    snapshot.financial_file_id = file_id
    snapshot.snapshot_version = 1
    snapshot.reporting_period_id = None
    snapshot.payload = sample_scenario_snapshot_payload()
    snapshot_repo.get_latest_snapshot_for_file.return_value = snapshot

    pending_run = MagicMock()
    pending_run.id = run_id
    pending_run.runtime_metadata = {}
    completed_run = MagicMock()
    completed_run.id = run_id
    completed_run.runtime_metadata = {
        "facts_contract": {},
        "scenario_provenance": {"archetype": "spending_reduction"},
    }
    analysis_service.create_run.return_value = pending_run
    analysis_service.complete_run.return_value = completed_run

    service = ScenarioService(
        session,
        analysis_service,
        analysis_repo,
        simulation_repo,
        snapshot_repo,
        financial_repo,
        organization_repo,
        waste_repo,
    )
    outcome = service.execute_scenario(
        org_id, scenario_id, source_file_id=file_id
    )

    assert outcome.analysis_run is completed_run
    assert outcome.facts_contract.engine_id == "scenario"
    simulation_repo.set_forecast_summary.assert_called_once()
    analysis_service.complete_run.assert_called_once()


def test_execute_rejects_unready_file(
    org_id: uuid.UUID, scenario_id: uuid.UUID, file_id: uuid.UUID
) -> None:
    initialize_business_engines()
    simulation_repo = MagicMock()
    simulation_repo.get_scenario.return_value = _mock_scenario(org_id, scenario_id)
    financial_repo = MagicMock()
    file = MagicMock()
    file.organization_id = org_id
    file.processing_status = ProcessingStatus.PENDING
    financial_repo.get_file.return_value = file

    service = ScenarioService(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        simulation_repo,
        MagicMock(),
        financial_repo,
        MagicMock(),
        MagicMock(),
    )
    with pytest.raises(InvalidStateError):
        service.execute_scenario(org_id, scenario_id, source_file_id=file_id)
