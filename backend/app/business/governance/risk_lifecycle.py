"""Approved governance transition maps (Sprint 9.4).

Finding lifecycle (analytical layer):
    detected → under_review → reviewed → promoted
    detected/under_review → dismissed; dismissed → detected (reopen)

Register lifecycle (enterprise governance):
    accepted → monitoring → mitigated → resolved → archived
    mitigated/resolved may reopen to monitoring

Legacy ``risks.status`` (active/in_progress/closed) is synced for backward
compatibility with existing RiskService APIs per architecture §4.3.
"""

from __future__ import annotations

from app.db.models.enums import (
    EnterpriseRiskLifecycleStatus,
    RiskFindingStatus,
    RiskStatus,
)

FINDING_TRANSITIONS: dict[str, set[str]] = {
    RiskFindingStatus.DETECTED: {
        RiskFindingStatus.UNDER_REVIEW,
        RiskFindingStatus.REVIEWED,
        RiskFindingStatus.DISMISSED,
    },
    RiskFindingStatus.UNDER_REVIEW: {
        RiskFindingStatus.REVIEWED,
        RiskFindingStatus.DISMISSED,
        RiskFindingStatus.DETECTED,
    },
    RiskFindingStatus.REVIEWED: {
        RiskFindingStatus.PROMOTED,
        RiskFindingStatus.DISMISSED,
        RiskFindingStatus.DETECTED,
    },
    RiskFindingStatus.PROMOTED: set(),
    RiskFindingStatus.DISMISSED: {RiskFindingStatus.DETECTED},
}

LIFECYCLE_TRANSITIONS: dict[str, set[str]] = {
    EnterpriseRiskLifecycleStatus.ACCEPTED: {EnterpriseRiskLifecycleStatus.MONITORING},
    EnterpriseRiskLifecycleStatus.MONITORING: {
        EnterpriseRiskLifecycleStatus.MITIGATED,
        EnterpriseRiskLifecycleStatus.RESOLVED,
        EnterpriseRiskLifecycleStatus.ACCEPTED,
    },
    EnterpriseRiskLifecycleStatus.MITIGATED: {
        EnterpriseRiskLifecycleStatus.RESOLVED,
        EnterpriseRiskLifecycleStatus.MONITORING,
    },
    EnterpriseRiskLifecycleStatus.RESOLVED: {
        EnterpriseRiskLifecycleStatus.ARCHIVED,
        EnterpriseRiskLifecycleStatus.MONITORING,
    },
    EnterpriseRiskLifecycleStatus.ARCHIVED: set(),
}

LIFECYCLE_TO_LEGACY_STATUS: dict[str, str] = {
    EnterpriseRiskLifecycleStatus.ACCEPTED: RiskStatus.ACTIVE,
    EnterpriseRiskLifecycleStatus.MONITORING: RiskStatus.IN_PROGRESS,
    EnterpriseRiskLifecycleStatus.MITIGATED: RiskStatus.IN_PROGRESS,
    EnterpriseRiskLifecycleStatus.RESOLVED: RiskStatus.IN_PROGRESS,
    EnterpriseRiskLifecycleStatus.ARCHIVED: RiskStatus.CLOSED,
}

PROMOTABLE_FINDING_STATUSES = {RiskFindingStatus.REVIEWED}
