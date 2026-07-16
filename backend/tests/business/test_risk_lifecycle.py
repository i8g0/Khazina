"""Enterprise risk lifecycle transition unit tests."""

from __future__ import annotations

import pytest

from app.business.governance.risk_lifecycle import (
    FINDING_TRANSITIONS,
    LIFECYCLE_TRANSITIONS,
    LIFECYCLE_TO_LEGACY_STATUS,
)
from app.db.models.enums import (
    EnterpriseRiskLifecycleStatus,
    RiskFindingStatus,
    RiskStatus,
)


def test_finding_detected_to_reviewed_path() -> None:
    assert RiskFindingStatus.REVIEWED in FINDING_TRANSITIONS[RiskFindingStatus.DETECTED]
    assert RiskFindingStatus.UNDER_REVIEW in FINDING_TRANSITIONS[RiskFindingStatus.DETECTED]


def test_finding_promoted_is_terminal() -> None:
    assert FINDING_TRANSITIONS[RiskFindingStatus.PROMOTED] == set()


def test_lifecycle_accepted_to_monitoring() -> None:
    assert (
        EnterpriseRiskLifecycleStatus.MONITORING
        in LIFECYCLE_TRANSITIONS[EnterpriseRiskLifecycleStatus.ACCEPTED]
    )


def test_lifecycle_archived_is_terminal() -> None:
    assert LIFECYCLE_TRANSITIONS[EnterpriseRiskLifecycleStatus.ARCHIVED] == set()


def test_lifecycle_syncs_legacy_status() -> None:
    assert (
        LIFECYCLE_TO_LEGACY_STATUS[EnterpriseRiskLifecycleStatus.ARCHIVED]
        == RiskStatus.CLOSED
    )
    assert (
        LIFECYCLE_TO_LEGACY_STATUS[EnterpriseRiskLifecycleStatus.MONITORING]
        == RiskStatus.IN_PROGRESS
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (EnterpriseRiskLifecycleStatus.ACCEPTED, EnterpriseRiskLifecycleStatus.ARCHIVED),
        (EnterpriseRiskLifecycleStatus.ARCHIVED, EnterpriseRiskLifecycleStatus.MONITORING),
    ],
)
def test_invalid_lifecycle_pairs_not_allowed(current: str, target: str) -> None:
    assert target not in LIFECYCLE_TRANSITIONS[current]
