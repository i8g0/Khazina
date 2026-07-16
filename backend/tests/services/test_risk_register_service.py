"""RiskRegisterService unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.db.models.enums import (
    EnterpriseRiskLifecycleStatus,
    RiskFindingStatus,
    RiskReviewAction,
    RiskStatus,
)
from app.services.exceptions import InvalidStateError, InvalidStateTransitionError
from app.services.risk_register import RiskRegisterService


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def finding_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def run_id() -> uuid.UUID:
    return uuid.uuid4()


def _service_with_mocks() -> tuple[RiskRegisterService, dict[str, MagicMock]]:
    session = MagicMock()
    mocks = {
        "session": session,
        "risks": MagicMock(),
        "risk_analysis": MagicMock(),
        "events": MagicMock(),
        "analyses": MagicMock(),
        "organizations": MagicMock(),
        "departments": MagicMock(),
    }
    service = RiskRegisterService(
        session,
        mocks["risks"],
        mocks["risk_analysis"],
        mocks["events"],
        mocks["analyses"],
        mocks["organizations"],
        mocks["departments"],
    )
    return service, mocks


def _finding(
    org_id: uuid.UUID,
    finding_id: uuid.UUID,
    run_id: uuid.UUID,
    *,
    status: str = RiskFindingStatus.REVIEWED,
) -> MagicMock:
    finding = MagicMock()
    finding.id = finding_id
    finding.organization_id = org_id
    finding.analysis_run_id = run_id
    finding.category_code = "liquidity"
    finding.name = "Liquidity stress"
    finding.description = "Low runway"
    finding.likelihood = "high"
    finding.impact = "high"
    finding.score = 85
    finding.priority = "high"
    finding.detection_rule_id = "liquidity.runway"
    finding.evidence = {"metric": "liquidity_ratio"}
    finding.department_id = None
    finding.finding_status = status
    finding.promoted_risk_id = None
    finding.created_at = datetime.now(UTC)
    return finding


def test_promote_finding_requires_reviewed_status(
    org_id: uuid.UUID,
    finding_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    service, mocks = _service_with_mocks()
    finding = _finding(org_id, finding_id, run_id, status=RiskFindingStatus.DETECTED)
    mocks["risk_analysis"].get_finding.return_value = finding

    with pytest.raises(InvalidStateError):
        service.promote_finding(org_id, finding_id)

    mocks["risks"].create.assert_not_called()


def test_promote_finding_creates_provenance_risk(
    org_id: uuid.UUID,
    finding_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    service, mocks = _service_with_mocks()
    finding = _finding(org_id, finding_id, run_id)
    run = MagicMock()
    run.id = run_id
    run.reporting_period_id = None
    run.source_snapshot_id = uuid.uuid4()
    result = MagicMock()
    result.source_snapshot_id = run.source_snapshot_id

    mocks["risk_analysis"].get_finding.return_value = finding
    mocks["risks"].get_by_source_finding_id.return_value = None
    mocks["analyses"].get.return_value = run
    mocks["risk_analysis"].get_result_for_run.return_value = result
    mocks["risks"].create.side_effect = lambda risk: risk
    mocks["risk_analysis"].update_finding.side_effect = lambda f, v: f
    mocks["events"].append.side_effect = lambda event: event

    outcome = service.promote_finding(org_id, finding_id, actor_user_id=uuid.uuid4())

    assert outcome.risk.source_type == "engine"
    assert outcome.risk.source_finding_id == finding_id
    assert outcome.risk.source_analysis_run_id == run_id
    assert outcome.risk.source_snapshot_id == run.source_snapshot_id
    assert outcome.risk.lifecycle_status == EnterpriseRiskLifecycleStatus.ACCEPTED
    assert outcome.risk.status == RiskStatus.ACTIVE
    mocks["risks"].create.assert_called_once()
    assert mocks["events"].append.call_count >= 2


def test_review_finding_approve_moves_to_reviewed(
    org_id: uuid.UUID,
    finding_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    service, mocks = _service_with_mocks()
    finding = _finding(org_id, finding_id, run_id, status=RiskFindingStatus.UNDER_REVIEW)
    mocks["risk_analysis"].get_finding.return_value = finding
    mocks["risk_analysis"].update_finding.side_effect = lambda f, v: f
    mocks["events"].append.side_effect = lambda event: event

    updated = service.review_finding(
        org_id,
        finding_id,
        RiskReviewAction.APPROVE,
        actor_user_id=uuid.uuid4(),
    )

    assert updated.finding_status == RiskFindingStatus.REVIEWED
    mocks["events"].append.assert_called_once()


def test_review_finding_rejects_invalid_transition(
    org_id: uuid.UUID,
    finding_id: uuid.UUID,
    run_id: uuid.UUID,
) -> None:
    service, mocks = _service_with_mocks()
    finding = _finding(org_id, finding_id, run_id, status=RiskFindingStatus.PROMOTED)
    mocks["risk_analysis"].get_finding.return_value = finding

    with pytest.raises(InvalidStateError):
        service.review_finding(org_id, finding_id, RiskReviewAction.REOPEN)


def test_update_lifecycle_rejects_invalid_transition(org_id: uuid.UUID) -> None:
    service, mocks = _service_with_mocks()
    risk = MagicMock()
    risk.id = uuid.uuid4()
    risk.organization_id = org_id
    risk.lifecycle_status = EnterpriseRiskLifecycleStatus.ACCEPTED
    risk.status = RiskStatus.ACTIVE
    mocks["risks"].get.return_value = risk

    with pytest.raises(InvalidStateTransitionError):
        service.update_lifecycle_status(
            org_id,
            risk.id,
            EnterpriseRiskLifecycleStatus.ARCHIVED,
        )


def test_update_lifecycle_archived_blocks_further_changes(org_id: uuid.UUID) -> None:
    service, mocks = _service_with_mocks()
    risk = MagicMock()
    risk.id = uuid.uuid4()
    risk.organization_id = org_id
    risk.lifecycle_status = EnterpriseRiskLifecycleStatus.ARCHIVED
    mocks["risks"].get.return_value = risk

    with pytest.raises(InvalidStateError):
        service.update_lifecycle_status(
            org_id,
            risk.id,
            EnterpriseRiskLifecycleStatus.MONITORING,
        )
