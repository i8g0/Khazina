"""ReportBuilderService orchestration tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.db.models.enums import AnalysisRunStatus, AnalysisType
from app.reports.loaders import ReportInputLoader
from app.reports.service import ReportBuilderService
from app.services.exceptions import InvalidStateError, ResourceNotFoundError
from tests.reports.conftest import (
    mock_breakdown,
    mock_waste_result,
    mock_waste_run,
    sample_waste_facts,
)


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def run_id() -> uuid.UUID:
    return uuid.uuid4()


def _build_service(
    org_id: uuid.UUID,
    run_id: uuid.UUID,
    *,
    with_ai: bool = True,
) -> ReportBuilderService:
    session = MagicMock()
    report_repo = MagicMock()
    analysis_repo = MagicMock()
    waste_repo = MagicMock()
    simulation_repo = MagicMock()
    recommendation_repo = MagicMock()
    organization_repo = MagicMock()
    financial_repo = MagicMock()

    run = mock_waste_run(org_id, run_id, with_ai=with_ai)
    analysis_repo.get.return_value = run
    waste_repo.get_result_for_run.return_value = mock_waste_result(run_id)
    waste_repo.list_category_breakdowns.return_value = [mock_breakdown(run_id)]
    waste_repo.list_vendor_findings.return_value = []
    recommendation_repo.list_for_analysis_run.return_value = []

    org = MagicMock()
    org.name = "Khazina Org"
    organization_repo.get_organization.return_value = org
    period = MagicMock()
    period.label = "2026-Q2"
    organization_repo.get_reporting_period.return_value = period
    file = MagicMock()
    file.file_name = "Budget.xlsx"
    financial_repo.get_file.return_value = file

    fixed_report_id = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
    created_report = MagicMock()
    created_report.id = fixed_report_id
    created_report.content_representation = None

    def create_side_effect(report: MagicMock) -> MagicMock:
        report.id = fixed_report_id
        return report

    report_repo.create.side_effect = create_side_effect

    loader = ReportInputLoader(
        analysis_repo,
        waste_repo,
        simulation_repo,
        recommendation_repo,
        organization_repo,
        financial_repo,
    )
    return ReportBuilderService(
        session,
        report_repo,
        analysis_repo,
        waste_repo,
        simulation_repo,
        recommendation_repo,
        organization_repo,
        financial_repo,
        input_loader=loader,
    )


def test_generate_waste_report_success(org_id: uuid.UUID, run_id: uuid.UUID) -> None:
    service = _build_service(org_id, run_id)
    fixed_ts = datetime(2026, 7, 15, 12, 0, tzinfo=UTC)
    outcome = service.generate_report(
        org_id, run_id, generated_at=fixed_ts
    )
    assert outcome.report.id is not None
    assert outcome.content.profile == "waste_decision"
    assert "cover" in [s.key for s in outcome.content.sections]
    assert outcome.export_serialization
    service._reports.create.assert_called_once()
    service._reports.update.assert_called_once()


def test_generate_rejects_incomplete_run(org_id: uuid.UUID, run_id: uuid.UUID) -> None:
    service = _build_service(org_id, run_id)
    run = service._analyses.get.return_value
    run.status = AnalysisRunStatus.PROCESSING
    with pytest.raises(InvalidStateError):
        service.generate_report(org_id, run_id)


def test_generate_rejects_unsupported_type(org_id: uuid.UUID, run_id: uuid.UUID) -> None:
    service = _build_service(org_id, run_id)
    run = service._analyses.get.return_value
    run.analysis_type = "legacy_unknown"
    with pytest.raises(InvalidStateError):
        service.generate_report(org_id, run_id)


def test_generate_risk_report_success(org_id: uuid.UUID, run_id: uuid.UUID) -> None:
    session = MagicMock()
    report_repo = MagicMock()
    analysis_repo = MagicMock()
    waste_repo = MagicMock()
    simulation_repo = MagicMock()
    recommendation_repo = MagicMock()
    organization_repo = MagicMock()
    financial_repo = MagicMock()
    risk_analysis_repo = MagicMock()
    risk_repo = MagicMock()

    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.analysis_type = AnalysisType.RISK
    run.status = AnalysisRunStatus.COMPLETED
    run.title = "Risk Run"
    run.source_file_id = uuid.uuid4()
    run.source_snapshot_id = uuid.uuid4()
    run.reporting_period_id = None
    run.completed_at = datetime(2026, 7, 16, tzinfo=UTC)
    run.runtime_metadata = {
        "facts_contract": sample_waste_facts().to_dict() | {"engine_id": "risk"},
    }
    analysis_repo.get.return_value = run

    risk_result = MagicMock()
    risk_result.id = uuid.uuid4()
    risk_result.overall_posture_level = "elevated"
    risk_result.total_findings = 3
    risk_result.high_priority_count = 1
    risk_result.medium_priority_count = 1
    risk_result.low_priority_count = 1
    risk_result.top_category_code = "financial"
    risk_analysis_repo.get_result_for_run.return_value = risk_result
    risk_analysis_repo.list_findings.return_value = []
    risk_repo.list_for_organization.return_value = []
    risk_repo.list_mitigation_plans_for_organization.return_value = []
    recommendation_repo.list_for_analysis_run.return_value = []

    org = MagicMock()
    org.name = "Khazina Org"
    organization_repo.get_organization.return_value = org
    financial_repo.get_file.return_value = MagicMock(file_name="Budget.xlsx")

    fixed_report_id = uuid.uuid4()
    report_repo.create.side_effect = lambda report: setattr(report, "id", fixed_report_id) or report

    facts = sample_waste_facts().to_dict()
    facts["engine_id"] = "risk"
    run.runtime_metadata = {"facts_contract": facts}

    loader = ReportInputLoader(
        analysis_repo,
        waste_repo,
        simulation_repo,
        recommendation_repo,
        organization_repo,
        financial_repo,
        risk_analysis_repo,
        risk_repo,
    )
    service = ReportBuilderService(
        session,
        report_repo,
        analysis_repo,
        waste_repo,
        simulation_repo,
        recommendation_repo,
        organization_repo,
        financial_repo,
        risk_analysis_repository=risk_analysis_repo,
        risk_repository=risk_repo,
        input_loader=loader,
    )
    fixed_ts = datetime(2026, 7, 16, 12, 0, tzinfo=UTC)
    outcome = service.generate_report(org_id, run_id, generated_at=fixed_ts)
    assert outcome.content.profile == "risk"
    assert "risk_summary" in [s.key for s in outcome.content.sections]


def test_generate_rejects_missing_run(org_id: uuid.UUID, run_id: uuid.UUID) -> None:
    service = _build_service(org_id, run_id)
    service._analyses.get.return_value = None
    with pytest.raises(ResourceNotFoundError):
        service.generate_report(org_id, run_id)


def test_deterministic_generation(org_id: uuid.UUID, run_id: uuid.UUID) -> None:
    fixed_org = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    fixed_run = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    service_a = _build_service(fixed_org, fixed_run, with_ai=False)
    service_b = _build_service(fixed_org, fixed_run, with_ai=False)
    fixed_ts = datetime(2026, 7, 15, 12, 0, tzinfo=UTC)
    out_a = service_a.generate_report(fixed_org, fixed_run, generated_at=fixed_ts)
    out_b = service_b.generate_report(fixed_org, fixed_run, generated_at=fixed_ts)
    assert out_a.export_serialization == out_b.export_serialization
