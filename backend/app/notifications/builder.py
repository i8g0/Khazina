"""Notification Builder — deterministic materialization from Platform Events."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AnalysisRun, Notification, Report
from app.db.models.enums import AnalysisType, RelatedEntityType
from app.db.models.notification import NotificationReadReceipt
from app.notifications.constants import (
    KIND_AI_RECOMMENDATIONS_COMPLETED,
    KIND_RISK_AI_RECOMMENDATIONS_COMPLETED,
    KIND_ANALYSIS_COMPLETED,
    KIND_ANALYSIS_FAILED,
    KIND_REPORT_GENERATED,
    KIND_REPORT_PUBLISHED,
    KIND_SCENARIO_COMPLETED,
    KIND_SCENARIO_FAILED,
    NOTIFICATION_VERSION,
    STATUS_ACTIVE,
)
from app.notifications.effective_preferences import (
    is_effective_notification_materialization_enabled,
)
from app.notifications.fingerprint import compute_event_fingerprint
from app.notifications.models import PersistedUserNotificationPreferences
from app.notifications.user_preferences_resolver import (
    resolve_user_notification_preferences,
)
from app.notifications.templates import (
    ai_recommendations_completed_message,
    risk_ai_recommendations_completed_message,
    analysis_completed_message,
    analysis_failed_message,
    build_payload_representation,
    report_generated_message,
    report_published_message,
    scenario_completed_message,
    scenario_failed_message,
)
from app.repositories import (
    AnalysisRepository,
    NotificationRepository,
    OrganizationRepository,
    RecommendationRepository,
    ReportRepository,
    SimulationRepository,
    UserNotificationPreferencesRepository,
    UserRepository,
)
from app.services.base import BaseService
from app.settings.service import SettingsService

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class MaterializedNotification:
    notification: Notification
    created: bool


class NotificationBuilder(BaseService):
    """Maps persisted Platform Events to notification records — no AI, no engines."""

    def __init__(
        self,
        session: Session,
        notification_repository: NotificationRepository,
        analysis_repository: AnalysisRepository,
        report_repository: ReportRepository,
        recommendation_repository: RecommendationRepository,
        simulation_repository: SimulationRepository,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
        *,
        settings_service: SettingsService | None = None,
        user_preferences_repository: UserNotificationPreferencesRepository | None = None,
    ) -> None:
        super().__init__(session)
        self._notifications = notification_repository
        self._analyses = analysis_repository
        self._reports = report_repository
        self._recommendations = recommendation_repository
        self._simulations = simulation_repository
        self._organizations = organization_repository
        self._users = user_repository
        self._settings = settings_service
        self._user_preferences = user_preferences_repository

    def materialize_analysis_completion(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        initiating_user_id: uuid.UUID | None,
    ) -> MaterializedNotification | None:
        if initiating_user_id is None:
            return None
        run = self._analyses.get(analysis_run_id)
        if run is None or run.organization_id != organization_id:
            return None
        if run.analysis_type == AnalysisType.FINANCIAL_WASTE:
            kind = KIND_ANALYSIS_COMPLETED
        elif run.analysis_type == AnalysisType.SIMULATION:
            kind = KIND_SCENARIO_COMPLETED
        else:
            return None
        if not self._gate_allows(organization_id, kind, initiating_user_id):
            return None
        period_label = self._period_label(run.reporting_period_id)
        if kind == KIND_SCENARIO_COMPLETED:
            title, body = self._scenario_templates(run, period_label)
            metadata = self._scenario_metadata(run)
        else:
            title, body = analysis_completed_message(
                run_title=run.title,
                period_label=period_label,
            )
            metadata = {"analysis_type": run.analysis_type}
        return self._persist(
            organization_id=organization_id,
            recipient_user_id=initiating_user_id,
            platform_event_kind=kind,
            title=title,
            body=body,
            source_entity_type=RelatedEntityType.ANALYSIS_RUN,
            source_entity_id=run.id,
            reporting_period_id=run.reporting_period_id,
            source_marker=f"completed:{run.completed_at.isoformat() if run.completed_at else 'unknown'}",
            metadata=metadata,
        )

    def materialize_ai_recommendations_completion(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        initiating_user_id: uuid.UUID | None,
        recommendation_count: int,
    ) -> MaterializedNotification | None:
        if initiating_user_id is None:
            return None
        if not self._gate_allows(
            organization_id, KIND_AI_RECOMMENDATIONS_COMPLETED, initiating_user_id
        ):
            return None
        run = self._analyses.get(analysis_run_id)
        if run is None or run.organization_id != organization_id:
            return None
        metadata = run.runtime_metadata or {}
        if not metadata.get("ai_insights"):
            return None
        title, body = ai_recommendations_completed_message(
            run_title=run.title,
            recommendation_count=recommendation_count,
        )
        ai_insights = metadata.get("ai_insights") or {}
        return self._persist(
            organization_id=organization_id,
            recipient_user_id=initiating_user_id,
            platform_event_kind=KIND_AI_RECOMMENDATIONS_COMPLETED,
            title=title,
            body=body,
            source_entity_type=RelatedEntityType.ANALYSIS_RUN,
            source_entity_id=run.id,
            reporting_period_id=run.reporting_period_id,
            source_marker=f"ai:{ai_insights.get('generated_at', 'unknown')}",
            metadata={
                "recommendation_count": recommendation_count,
                "model": ai_insights.get("model"),
                "prompt_version": ai_insights.get("prompt_version"),
            },
        )

    def materialize_risk_ai_recommendations_completion(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        initiating_user_id: uuid.UUID | None,
        recommendation_count: int,
    ) -> MaterializedNotification | None:
        if initiating_user_id is None:
            return None
        if not self._gate_allows(
            organization_id, KIND_RISK_AI_RECOMMENDATIONS_COMPLETED, initiating_user_id
        ):
            return None
        run = self._analyses.get(analysis_run_id)
        if run is None or run.organization_id != organization_id:
            return None
        metadata = run.runtime_metadata or {}
        ai_insights = metadata.get("ai_insights") or {}
        if not ai_insights or ai_insights.get("domain") != "risk":
            return None
        title, body = risk_ai_recommendations_completed_message(
            run_title=run.title,
            recommendation_count=recommendation_count,
        )
        return self._persist(
            organization_id=organization_id,
            recipient_user_id=initiating_user_id,
            platform_event_kind=KIND_RISK_AI_RECOMMENDATIONS_COMPLETED,
            title=title,
            body=body,
            source_entity_type=RelatedEntityType.ANALYSIS_RUN,
            source_entity_id=run.id,
            reporting_period_id=run.reporting_period_id,
            source_marker=f"risk_ai:{ai_insights.get('generated_at', 'unknown')}",
            metadata={
                "recommendation_count": recommendation_count,
                "model": ai_insights.get("model"),
                "prompt_version": ai_insights.get("prompt_version"),
                "domain": "risk",
            },
        )

    def materialize_report_generated(
        self,
        organization_id: uuid.UUID,
        report_id: uuid.UUID,
        *,
        initiating_user_id: uuid.UUID | None,
    ) -> MaterializedNotification | None:
        if initiating_user_id is None:
            return None
        if not self._gate_allows(
            organization_id, KIND_REPORT_GENERATED, initiating_user_id
        ):
            return None
        report = self._reports.get(report_id)
        if report is None or report.organization_id != organization_id:
            return None
        title, body = report_generated_message(
            report_title=report.title,
            report_type=report.report_type,
        )
        return self._persist(
            organization_id=organization_id,
            recipient_user_id=initiating_user_id,
            platform_event_kind=KIND_REPORT_GENERATED,
            title=title,
            body=body,
            source_entity_type=RelatedEntityType.REPORT,
            source_entity_id=report.id,
            reporting_period_id=report.reporting_period_id,
            source_marker=f"draft:{report.id}",
            metadata={"report_type": report.report_type, "status": report.status},
        )

    def materialize_report_published(
        self,
        organization_id: uuid.UUID,
        report_id: uuid.UUID,
        *,
        initiating_user_id: uuid.UUID | None,
    ) -> MaterializedNotification | None:
        if initiating_user_id is None:
            return None
        if not self._gate_allows(
            organization_id, KIND_REPORT_PUBLISHED, initiating_user_id
        ):
            return None
        report = self._reports.get(report_id)
        if report is None or report.organization_id != organization_id:
            return None
        title, body = report_published_message(
            report_title=report.title,
            report_type=report.report_type,
        )
        published_marker = (
            report.published_at.isoformat() if report.published_at else "unknown"
        )
        return self._persist(
            organization_id=organization_id,
            recipient_user_id=initiating_user_id,
            platform_event_kind=KIND_REPORT_PUBLISHED,
            title=title,
            body=body,
            source_entity_type=RelatedEntityType.REPORT,
            source_entity_id=report.id,
            reporting_period_id=report.reporting_period_id,
            source_marker=f"ready:{published_marker}",
            metadata={"report_type": report.report_type, "published_at": published_marker},
        )

    def materialize_analysis_failure(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        initiating_user_id: uuid.UUID | None,
    ) -> MaterializedNotification | None:
        if initiating_user_id is None:
            return None
        run = self._analyses.get(analysis_run_id)
        if run is None or run.organization_id != organization_id:
            return None
        if run.analysis_type == AnalysisType.FINANCIAL_WASTE:
            kind = KIND_ANALYSIS_FAILED
        elif run.analysis_type == AnalysisType.SIMULATION:
            kind = KIND_SCENARIO_FAILED
        else:
            return None
        if not self._gate_allows(organization_id, kind, initiating_user_id):
            return None
        metadata = run.runtime_metadata or {}
        failure = dict(metadata.get("failure") or {})
        error_code = failure.get("error_code")
        if kind == KIND_SCENARIO_FAILED:
            title, body = scenario_failed_message(
                run_title=run.title,
                error_code=str(error_code) if error_code else None,
            )
        else:
            title, body = analysis_failed_message(
                run_title=run.title,
                error_code=str(error_code) if error_code else None,
            )
        failed_marker = (
            run.completed_at.isoformat() if run.completed_at else "unknown"
        )
        return self._persist(
            organization_id=organization_id,
            recipient_user_id=initiating_user_id,
            platform_event_kind=kind,
            title=title,
            body=body,
            source_entity_type=RelatedEntityType.ANALYSIS_RUN,
            source_entity_id=run.id,
            reporting_period_id=run.reporting_period_id,
            source_marker=f"failed:{failed_marker}",
            metadata={"analysis_type": run.analysis_type, "failure": failure},
        )

    def _persist(
        self,
        *,
        organization_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
        platform_event_kind: str,
        title: str,
        body: str,
        source_entity_type: str,
        source_entity_id: uuid.UUID,
        reporting_period_id: uuid.UUID | None,
        source_marker: str,
        metadata: dict[str, Any],
    ) -> MaterializedNotification | None:
        if not self._validate_recipient(organization_id, recipient_user_id):
            return None
        fingerprint = compute_event_fingerprint(
            platform_event_kind=platform_event_kind,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            recipient_user_id=recipient_user_id,
            source_marker=source_marker,
        )
        existing = self._notifications.get_by_fingerprint(fingerprint)
        if existing is not None:
            return MaterializedNotification(notification=existing, created=False)

        materialized_at = datetime.now(timezone.utc)
        payload = build_payload_representation(
            platform_event_kind=platform_event_kind,
            title=title,
            body=body,
            source_entity_type=source_entity_type,
            source_entity_id=str(source_entity_id),
            metadata=metadata,
        )
        payload["notification_version"] = NOTIFICATION_VERSION

        notification = Notification(
            organization_id=organization_id,
            recipient_user_id=recipient_user_id,
            platform_event_kind=platform_event_kind,
            title=title,
            body=body,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            reporting_period_id=reporting_period_id,
            event_fingerprint=fingerprint,
            payload_representation=payload,
            materialized_at=materialized_at,
            status=STATUS_ACTIVE,
        )
        with self._transaction():
            self._notifications.create(notification)
        return MaterializedNotification(notification=notification, created=True)

    def _validate_recipient(
        self, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        user = self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            return False
        if user.organization_id != organization_id:
            return False
        return True

    def _gate_allows(
        self,
        organization_id: uuid.UUID,
        kind: str,
        recipient_user_id: uuid.UUID,
    ) -> bool:
        if self._settings is None:
            return True
        resolved = self._settings.get_resolved_settings(organization_id)
        user_prefs = None
        if self._user_preferences is not None:
            record = self._user_preferences.get_by_user(
                organization_id, recipient_user_id
            )
            if record is not None:
                user_prefs = resolve_user_notification_preferences(
                    PersistedUserNotificationPreferences.from_dict(
                        record.preferences_document
                    )
                )
        return is_effective_notification_materialization_enabled(
            resolved, user_prefs, kind
        )

    def _period_label(self, reporting_period_id: uuid.UUID | None) -> str | None:
        if reporting_period_id is None:
            return None
        period = self._organizations.get_reporting_period(reporting_period_id)
        return period.label if period else None

    def _scenario_templates(
        self, run: AnalysisRun, period_label: str | None
    ) -> tuple[str, str]:
        metadata = run.runtime_metadata or {}
        provenance = metadata.get("scenario_provenance") or {}
        scenario_name: str | None = None
        archetype = provenance.get("archetype")
        simulation_run = self._simulations.get_run_for_analysis_run(run.id)
        if simulation_run is not None:
            scenario_name = simulation_run.result_title
        return scenario_completed_message(
            run_title=run.title,
            scenario_name=scenario_name,
            archetype=str(archetype) if archetype else None,
            period_label=period_label,
        )

    def _scenario_metadata(self, run: AnalysisRun) -> dict[str, Any]:
        metadata = run.runtime_metadata or {}
        provenance = dict(metadata.get("scenario_provenance") or {})
        simulation_run = self._simulations.get_run_for_analysis_run(run.id)
        if simulation_run is not None:
            provenance.setdefault("result_title", simulation_run.result_title)
            provenance.setdefault("result_description", simulation_run.result_description)
        return provenance
