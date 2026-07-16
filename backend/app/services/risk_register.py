"""Enterprise Risk Register governance (Sprint 9.4)."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.business.governance.risk_lifecycle import (
    FINDING_TRANSITIONS,
    LIFECYCLE_TO_LEGACY_STATUS,
    LIFECYCLE_TRANSITIONS,
    PROMOTABLE_FINDING_STATUSES,
)
from app.core.logging import get_logger
from app.db.models import Risk, RiskEvent, RiskFinding
from app.db.models.enums import (
    EnterpriseRiskLifecycleStatus,
    RiskEventType,
    RiskFindingStatus,
    RiskReviewAction,
    RiskSourceType,
    RiskStatus,
)
from app.observability.structured_log import log_pipeline_event
from app.repositories import (
    AnalysisRepository,
    DepartmentRepository,
    OrganizationRepository,
    RiskAnalysisRepository,
    RiskEventRepository,
    RiskRepository,
)
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    InvalidStateError,
    InvalidStateTransitionError,
    ResourceNotFoundError,
)

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class PromotionOutcome:
    finding: RiskFinding
    risk: Risk
    event: RiskEvent


class RiskRegisterService(BaseService):
    """Governance layer: finding review, manual promotion, lifecycle, audit."""

    def __init__(
        self,
        session: Session,
        risk_repository: RiskRepository,
        risk_analysis_repository: RiskAnalysisRepository,
        risk_event_repository: RiskEventRepository,
        analysis_repository: AnalysisRepository,
        organization_repository: OrganizationRepository,
        department_repository: DepartmentRepository,
    ) -> None:
        super().__init__(session)
        self._risks = risk_repository
        self._risk_analysis = risk_analysis_repository
        self._events = risk_event_repository
        self._analyses = analysis_repository
        self._organizations = organization_repository
        self._departments = department_repository

    # -- finding review -------------------------------------------------------

    def review_finding(
        self,
        organization_id: uuid.UUID,
        finding_id: uuid.UUID,
        action: str,
        *,
        reason: str | None = None,
        actor_user_id: uuid.UUID | None = None,
    ) -> RiskFinding:
        finding = self._owned_finding(organization_id, finding_id)
        if action not in set(RiskReviewAction):
            raise BusinessValidationError(f"Unknown review action '{action}'")
        if finding.finding_status == RiskFindingStatus.PROMOTED:
            raise InvalidStateError("Promoted findings cannot be reviewed")

        target_status = self._finding_target_status(finding.finding_status, action)
        self._validate_finding_transition(finding.finding_status, target_status)
        from_status = finding.finding_status

        event_type = self._finding_event_type(action, target_status)
        with self._transaction():
            self._risk_analysis.update_finding(
                finding, {"finding_status": target_status}
            )
            self._record_event(
                organization_id,
                event_type=event_type,
                from_status=from_status,
                to_status=target_status,
                actor_user_id=actor_user_id,
                reason=reason,
                metadata={
                    "finding_id": str(finding.id),
                    "analysis_run_id": str(finding.analysis_run_id),
                    "action": action,
                },
            )

        self._log_governance(
            organization_id,
            action=f"finding_{action}",
            entity_type="finding",
            entity_id=str(finding.id),
            from_status=from_status,
            to_status=target_status,
            actor_user_id=actor_user_id,
            reason=reason,
        )
        finding.finding_status = target_status
        return finding

    # -- promotion ------------------------------------------------------------

    def promote_finding(
        self,
        organization_id: uuid.UUID,
        finding_id: uuid.UUID,
        *,
        owner_label: str | None = None,
        department_id: uuid.UUID | None = None,
        actor_user_id: uuid.UUID | None = None,
        reason: str | None = None,
    ) -> PromotionOutcome:
        """Manual promotion: reviewed finding → enterprise risk (never automatic)."""
        finding = self._owned_finding(organization_id, finding_id)
        if finding.finding_status not in PROMOTABLE_FINDING_STATUSES:
            raise InvalidStateError(
                "Only reviewed findings may be promoted to the register "
                f"(current status: '{finding.finding_status}')"
            )
        if finding.promoted_risk_id is not None:
            raise InvalidStateError("Finding has already been promoted")
        if self._risks.get_by_source_finding_id(finding.id) is not None:
            raise InvalidStateError("A register risk already exists for this finding")

        run = self._analyses.get(finding.analysis_run_id)
        if run is None:
            raise ResourceNotFoundError("AnalysisRun", finding.analysis_run_id)

        result = self._risk_analysis.get_result_for_run(run.id)
        snapshot_id = (
            result.source_snapshot_id
            if result is not None
            else run.source_snapshot_id
        )

        if department_id is not None:
            department = self._departments.get(department_id)
            if department is None:
                raise ResourceNotFoundError("Department", department_id)
            self._check_ownership(department, "Department", organization_id)

        risk = Risk(
            organization_id=organization_id,
            department_id=department_id or finding.department_id,
            reporting_period_id=run.reporting_period_id,
            name=finding.name,
            description=finding.description,
            priority=finding.priority,
            score=finding.score,
            status=RiskStatus.ACTIVE,
            lifecycle_status=EnterpriseRiskLifecycleStatus.ACCEPTED,
            owner_label=owner_label,
            likelihood=finding.likelihood,
            impact=finding.impact,
            category_label=finding.category_code,
            category_code=finding.category_code,
            source_type=RiskSourceType.ENGINE,
            source_analysis_run_id=run.id,
            source_finding_id=finding.id,
            source_snapshot_id=snapshot_id,
            detected_at=finding.created_at,
            last_updated_at=date.today(),
        )

        with self._transaction():
            self._risks.create(risk)
            self._risk_analysis.update_finding(
                finding,
                {
                    "finding_status": RiskFindingStatus.PROMOTED,
                    "promoted_risk_id": risk.id,
                },
            )
            registered_event = self._record_event(
                organization_id,
                event_type=RiskEventType.REGISTERED,
                from_status=None,
                to_status=EnterpriseRiskLifecycleStatus.ACCEPTED,
                actor_user_id=actor_user_id,
                reason=reason,
                risk_id=risk.id,
                metadata={
                    "source_finding_id": str(finding.id),
                    "source_analysis_run_id": str(run.id),
                    "source_snapshot_id": str(snapshot_id) if snapshot_id else None,
                    "detection_rule_id": finding.detection_rule_id,
                },
            )
            self._record_event(
                organization_id,
                event_type=RiskEventType.FINDING_PROMOTED,
                from_status=RiskFindingStatus.REVIEWED,
                to_status=RiskFindingStatus.PROMOTED,
                actor_user_id=actor_user_id,
                reason=reason,
                risk_id=risk.id,
                metadata={
                    "finding_id": str(finding.id),
                    "analysis_run_id": str(run.id),
                },
            )

        self._log_governance(
            organization_id,
            action="finding_promoted",
            entity_type="risk",
            entity_id=str(risk.id),
            from_status=RiskFindingStatus.REVIEWED,
            to_status=RiskFindingStatus.PROMOTED,
            actor_user_id=actor_user_id,
            reason=reason,
            finding_id=str(finding.id),
            analysis_run_id=str(run.id),
            snapshot_id=str(snapshot_id) if snapshot_id else None,
        )
        finding.finding_status = RiskFindingStatus.PROMOTED
        finding.promoted_risk_id = risk.id
        return PromotionOutcome(finding=finding, risk=risk, event=registered_event)

    # -- register lifecycle ---------------------------------------------------

    def update_lifecycle_status(
        self,
        organization_id: uuid.UUID,
        risk_id: uuid.UUID,
        new_lifecycle_status: str,
        *,
        reason: str | None = None,
        actor_user_id: uuid.UUID | None = None,
    ) -> Risk:
        risk = self._owned_risk(organization_id, risk_id)
        if new_lifecycle_status not in set(EnterpriseRiskLifecycleStatus):
            raise BusinessValidationError(
                f"Unknown lifecycle status '{new_lifecycle_status}'"
            )
        if risk.lifecycle_status == EnterpriseRiskLifecycleStatus.ARCHIVED:
            raise InvalidStateError("Archived enterprise risks cannot be modified")
        self._validate_lifecycle_transition(risk.lifecycle_status, new_lifecycle_status)

        legacy_status = LIFECYCLE_TO_LEGACY_STATUS[new_lifecycle_status]
        with self._transaction():
            self._risks.update(
                risk,
                {
                    "lifecycle_status": new_lifecycle_status,
                    "status": legacy_status,
                    "last_updated_at": date.today(),
                },
            )
            self._record_event(
                organization_id,
                event_type=RiskEventType.LIFECYCLE_TRANSITIONED,
                from_status=risk.lifecycle_status,
                to_status=new_lifecycle_status,
                actor_user_id=actor_user_id,
                reason=reason,
                risk_id=risk.id,
                metadata={"legacy_status": legacy_status},
            )

        self._log_governance(
            organization_id,
            action="lifecycle_transition",
            entity_type="risk",
            entity_id=str(risk.id),
            from_status=risk.lifecycle_status,
            to_status=new_lifecycle_status,
            actor_user_id=actor_user_id,
            reason=reason,
        )
        risk.lifecycle_status = new_lifecycle_status
        risk.status = legacy_status
        return risk

    def review_risk(
        self,
        organization_id: uuid.UUID,
        risk_id: uuid.UUID,
        action: str,
        *,
        reason: str | None = None,
        actor_user_id: uuid.UUID | None = None,
    ) -> Risk:
        risk = self._owned_risk(organization_id, risk_id)
        if action not in set(RiskReviewAction):
            raise BusinessValidationError(f"Unknown review action '{action}'")
        if risk.lifecycle_status == EnterpriseRiskLifecycleStatus.ARCHIVED:
            raise InvalidStateError("Archived enterprise risks cannot be reviewed")

        target = self._risk_lifecycle_target(risk.lifecycle_status, action)
        if target is None:
            raise InvalidStateError(
                f"Action '{action}' is not valid for lifecycle status "
                f"'{risk.lifecycle_status}'"
            )
        return self.update_lifecycle_status(
            organization_id,
            risk_id,
            target,
            reason=reason,
            actor_user_id=actor_user_id,
        )

    # -- queries --------------------------------------------------------------

    def get_risk(
        self, organization_id: uuid.UUID, risk_id: uuid.UUID
    ) -> Risk:
        return self._owned_risk(organization_id, risk_id)

    def list_risks(
        self,
        organization_id: uuid.UUID,
        *,
        status: str | None = None,
        lifecycle_status: str | None = None,
        priority: str | None = None,
        department_id: uuid.UUID | None = None,
        category_code: str | None = None,
        source_type: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Risk]:
        self._require_organization(organization_id)
        return self._risks.list_for_organization(
            organization_id,
            status=status,
            lifecycle_status=lifecycle_status,
            priority=priority,
            department_id=department_id,
            category_code=category_code,
            source_type=source_type,
            limit=limit,
            offset=offset,
        )

    def get_risk_history(
        self,
        organization_id: uuid.UUID,
        risk_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[RiskEvent]:
        self._owned_risk(organization_id, risk_id)
        return self._events.list_for_risk(risk_id, limit=limit, offset=offset)

    def get_finding_provenance(
        self, organization_id: uuid.UUID, risk_id: uuid.UUID
    ) -> dict[str, Any]:
        """Return full provenance chain: snapshot → run → finding → risk."""
        risk = self._owned_risk(organization_id, risk_id)
        finding = None
        if risk.source_finding_id is not None:
            finding = self._risk_analysis.get_finding(risk.source_finding_id)
        run = None
        if risk.source_analysis_run_id is not None:
            run = self._analyses.get(risk.source_analysis_run_id)
        return {
            "risk_id": risk.id,
            "source_type": risk.source_type,
            "source_snapshot_id": risk.source_snapshot_id,
            "source_analysis_run_id": risk.source_analysis_run_id,
            "source_finding_id": risk.source_finding_id,
            "detected_at": risk.detected_at,
            "finding": (
                {
                    "id": finding.id,
                    "name": finding.name,
                    "detection_rule_id": finding.detection_rule_id,
                    "score": finding.score,
                    "priority": finding.priority,
                }
                if finding is not None
                else None
            ),
            "analysis_run": (
                {
                    "id": run.id,
                    "title": run.title,
                    "status": run.status,
                    "source_snapshot_id": run.source_snapshot_id,
                }
                if run is not None
                else None
            ),
        }

    # -- internals ------------------------------------------------------------

    def _owned_finding(
        self, organization_id: uuid.UUID, finding_id: uuid.UUID
    ) -> RiskFinding:
        finding = self._risk_analysis.get_finding(finding_id)
        if finding is None:
            raise ResourceNotFoundError("RiskFinding", finding_id)
        self._check_ownership(finding, "RiskFinding", organization_id)
        return finding

    def _owned_risk(
        self, organization_id: uuid.UUID, risk_id: uuid.UUID
    ) -> Risk:
        risk = self._risks.get(risk_id)
        if risk is None:
            raise ResourceNotFoundError("Risk", risk_id)
        self._check_ownership(risk, "Risk", organization_id)
        return risk

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)

    @staticmethod
    def _validate_finding_transition(current: str, target: str) -> None:
        allowed = FINDING_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise InvalidStateTransitionError("RiskFinding", current, target)

    @staticmethod
    def _validate_lifecycle_transition(current: str, target: str) -> None:
        allowed = LIFECYCLE_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise InvalidStateTransitionError(
                "EnterpriseRisk", current, target
            )

    @staticmethod
    def _finding_target_status(current: str, action: str) -> str:
        if action == RiskReviewAction.APPROVE:
            return RiskFindingStatus.REVIEWED
        if action == RiskReviewAction.REJECT:
            return RiskFindingStatus.DISMISSED
        if action == RiskReviewAction.REQUEST_REVIEW:
            return RiskFindingStatus.UNDER_REVIEW
        if action == RiskReviewAction.DISMISS:
            return RiskFindingStatus.DISMISSED
        if action == RiskReviewAction.REOPEN:
            return RiskFindingStatus.DETECTED
        raise BusinessValidationError(f"Unsupported finding action '{action}'")

    @staticmethod
    def _finding_event_type(action: str, target_status: str) -> str:
        if target_status == RiskFindingStatus.DISMISSED:
            return RiskEventType.FINDING_DISMISSED
        return RiskEventType.FINDING_REVIEWED

    @staticmethod
    def _risk_lifecycle_target(current: str, action: str) -> str | None:
        if action == RiskReviewAction.APPROVE:
            mapping = {
                EnterpriseRiskLifecycleStatus.ACCEPTED: EnterpriseRiskLifecycleStatus.MONITORING,
                EnterpriseRiskLifecycleStatus.MONITORING: EnterpriseRiskLifecycleStatus.MITIGATED,
                EnterpriseRiskLifecycleStatus.MITIGATED: EnterpriseRiskLifecycleStatus.RESOLVED,
                EnterpriseRiskLifecycleStatus.RESOLVED: EnterpriseRiskLifecycleStatus.ARCHIVED,
            }
            return mapping.get(current)
        if action == RiskReviewAction.REJECT:
            if current == EnterpriseRiskLifecycleStatus.MONITORING:
                return EnterpriseRiskLifecycleStatus.ACCEPTED
            return None
        if action == RiskReviewAction.REQUEST_REVIEW:
            if current == EnterpriseRiskLifecycleStatus.ACCEPTED:
                return EnterpriseRiskLifecycleStatus.MONITORING
            return None
        if action == RiskReviewAction.REOPEN:
            if current in {
                EnterpriseRiskLifecycleStatus.MITIGATED,
                EnterpriseRiskLifecycleStatus.RESOLVED,
            }:
                return EnterpriseRiskLifecycleStatus.MONITORING
            return None
        return None

    def _record_event(
        self,
        organization_id: uuid.UUID,
        *,
        event_type: str,
        from_status: str | None,
        to_status: str | None,
        actor_user_id: uuid.UUID | None,
        reason: str | None,
        risk_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RiskEvent:
        event = RiskEvent(
            risk_id=risk_id,
            organization_id=organization_id,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            actor_user_id=actor_user_id,
            reason=reason.strip() if reason else None,
            event_metadata=metadata or {},
        )
        return self._events.append(event)

    @staticmethod
    def _log_governance(
        organization_id: uuid.UUID,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        from_status: str | None,
        to_status: str | None,
        actor_user_id: uuid.UUID | None,
        reason: str | None = None,
        **extra: Any,
    ) -> None:
        log_pipeline_event(
            logger,
            "governance_action",
            organization_id=str(organization_id),
            message=action,
            entity_type=entity_type,
            entity_id=entity_id,
            from_status=from_status,
            to_status=to_status,
            actor_user_id=str(actor_user_id) if actor_user_id else None,
            reason=reason,
            **extra,
        )
