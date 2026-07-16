"""AI Recommendation Service — orchestrates Facts-only AI generation (Sprint 6.4)."""

from __future__ import annotations

import logging
import time
import uuid

from app.ai.execution_trace import begin_trace
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.ai.client import OllamaClient
from app.ai.providers.base import AIProvider
from app.ai.providers.factory import create_ai_provider
from app.ai.exceptions import AIConnectionError, AITimeoutError
from app.ai.prompts.tasks import PromptTask
from app.ai_recommendations.constants import TASK_EXECUTION_ORDER
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.facts_loader import load_facts_contract, load_risk_facts_contract
from app.ai_recommendations.risk_constants import (
    RISK_RECOMMENDATION_TASK,
    RISK_TASK_EXECUTION_ORDER,
)
from app.ai_recommendations.risk_mapper import (
    build_risk_ai_insights_payload,
    parse_and_map_risk_recommendations,
)
from app.ai_recommendations.risk_metadata import build_risk_metadata_supplement
from app.ai_recommendations.risk_validator import validate_risk_task_results
from app.ai_recommendations.mapper import (
    build_ai_insights_payload,
    parse_and_map_recommendations,
)
from app.ai_recommendations.pipeline import AiTaskPipeline, TaskExecutionResult
from app.ai_recommendations.validator import validate_task_results
from app.ai_recommendations.waste_metadata import build_waste_metadata_supplement
from app.business.facts.contract import FactsContract
from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import AnalysisRun, Recommendation
from app.db.models.enums import AnalysisRunStatus, AnalysisType, RecommendationDomain
from app.repositories import (
    AnalysisRepository,
    RecommendationRepository,
    RiskAnalysisRepository,
    WasteRepository,
)
from app.services.base import BaseService
from app.services.exceptions import InvalidStateError, ResourceNotFoundError
from app.settings.exceptions import AiRecommendationsDisabledError
from app.settings.service import SettingsService
from app.notifications.builder import NotificationBuilder
from app.notifications.hooks import try_materialize
from app.observability.errors import classify_exception
from app.observability.pipeline import PipelineStage, PipelineTimeline, load_pipeline_timeline
from app.presentation.narrative_guard import (
    NARRATIVE_LLM_UNAVAILABLE,
    NARRATIVE_REJECTED,
    facts_only_insights_payload,
    guard_executive_summary_task,
    is_llm_transport_error,
    merge_task_results,
)

from app.observability.structured_log import log_pipeline_event

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class AiRecommendationOutcome:
    """Result of successful AI recommendation generation."""

    analysis_run: AnalysisRun
    facts_contract: FactsContract
    recommendations: tuple[Recommendation, ...]
    ai_insights: dict[str, Any]


class AiRecommendationService(BaseService):
    """Generates executive insights and recommendations from completed waste runs."""

    def __init__(
        self,
        session: Session,
        analysis_repository: AnalysisRepository,
        waste_repository: WasteRepository,
        recommendation_repository: RecommendationRepository,
        *,
        risk_analysis_repository: RiskAnalysisRepository | None = None,
        task_pipeline: AiTaskPipeline | None = None,
        ai_provider: AIProvider | None = None,
        ollama_client: OllamaClient | None = None,
        settings_service: SettingsService | None = None,
        notification_builder: NotificationBuilder | None = None,
    ) -> None:
        super().__init__(session)
        self._analyses = analysis_repository
        self._waste = waste_repository
        self._risk_analysis = risk_analysis_repository
        self._recommendation_repo = recommendation_repository
        self._model_name = settings.ai.active_model
        self._settings = settings_service
        self._notifications = notification_builder
        client = ai_provider or ollama_client or create_ai_provider(settings.ai)
        self._pipeline = task_pipeline or AiTaskPipeline(
            llm_client=client,
            llm_model=self._model_name,
            prompt_language=settings.ai.default_prompt_language,
        )

    def generate_waste_recommendations(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        regenerate: bool = False,
        initiating_user_id: uuid.UUID | None = None,
    ) -> AiRecommendationOutcome:
        run = self._analyses.get(analysis_run_id)
        if run is None:
            raise ResourceNotFoundError("AnalysisRun", analysis_run_id)
        self._check_ownership(run, "AnalysisRun", organization_id)
        self._validate_run_preconditions(run)
        prompt_language = self._resolve_prompt_language(organization_id)

        metadata = dict(run.runtime_metadata or {})
        if metadata.get("ai_insights") and not regenerate:
            raise AiRecommendationError(
                "ai_insights_already_exist",
                "AI insights already exist for this analysis run; "
                "pass regenerate=true to replace",
            )

        timeline = PipelineTimeline(
            organization_id=str(organization_id),
            file_id=str(run.source_file_id) if run.source_file_id else None,
            snapshot_id=str(run.source_snapshot_id) if run.source_snapshot_id else None,
            analysis_run_id=str(analysis_run_id),
            inherited=load_pipeline_timeline(metadata),
        )
        pipeline_started = time.perf_counter()
        trace = begin_trace(str(analysis_run_id), "waste")
        timeline.start_stage(PipelineStage.AI_STARTED)
        log_pipeline_event(
            logger,
            "pipeline_stage",
            stage=PipelineStage.AI_STARTED.value,
            status="started",
            organization_id=str(organization_id),
            analysis_run_id=str(analysis_run_id),
        )

        try:
            facts = load_facts_contract(metadata)
            trace.mark("facts_loaded")
            breakdowns = self._waste.list_category_breakdowns(analysis_run_id)
            vendors = self._waste.list_vendor_findings(analysis_run_id)
            supplement = build_waste_metadata_supplement(
                metadata,
                facts_contract=facts,
                gold_breakdowns=breakdowns,
                gold_vendors=vendors,
            )
            trace.mark(
                "settings_resolved",
                detail=f"lang={prompt_language} parallel={settings.ai.parallel_tasks_enabled} provider={settings.ai.ai_provider}",
            )
            try:
                task_results = self._execute_tasks(
                    facts,
                    prompt_language=prompt_language,
                    prompt_supplement=supplement,
                )
            except (AIConnectionError, AITimeoutError):
                generated_at = datetime.now(timezone.utc)
                ai_insights = facts_only_insights_payload(
                    facts=facts,
                    model_name=self._model_name,
                    domain="waste",
                    narrative_status=NARRATIVE_LLM_UNAVAILABLE,
                    generated_at_iso=generated_at.isoformat(),
                )
                timeline.complete_stage(PipelineStage.AI_COMPLETED)
                with self._transaction():
                    metadata["ai_insights"] = ai_insights
                    metadata["pipeline_timeline"] = timeline.to_list()
                    updated = self._analyses.update(run, {"runtime_metadata": metadata})
                trace.mark("persistence_completed")
                return AiRecommendationOutcome(
                    analysis_run=updated,
                    facts_contract=facts,
                    recommendations=(),
                    ai_insights=ai_insights,
                )

            trace.mark("llm_tasks_completed", detail=f"count={len(task_results)}")
            validate_task_results(task_results)
            generated_at = datetime.now(timezone.utc)

            exec_task = next(
                r for r in task_results if r.task == PromptTask.EXECUTIVE_SUMMARY
            )
            guarded_exec, exec_status = guard_executive_summary_task(
                exec_task,
                facts,
                self._pipeline,
                prompt_language=prompt_language,
                prompt_supplement=supplement,
            )
            task_results = merge_task_results(task_results, guarded_exec)

            rec_task = next(
                r for r in task_results if r.task == PromptTask.RECOMMENDATIONS
            )
            rec_payloads, rec_status = parse_and_map_recommendations(
                rec_task,
                facts,
                analysis_run_id,
                self._model_name,
                pipeline=self._pipeline,
                prompt_language=prompt_language,
                prompt_supplement=supplement,
            )
            snapshot_id = str(run.source_snapshot_id) if run.source_snapshot_id else None
            narrative_status = exec_status or rec_status
            ai_insights = build_ai_insights_payload(
                task_results=task_results,
                facts_contract=facts,
                model_name=self._model_name,
                source_snapshot_id=snapshot_id,
                generated_at=generated_at,
                narrative_status=narrative_status,
                omit_executive_summary=exec_status is not None,
            )

            timeline.complete_stage(PipelineStage.AI_COMPLETED)
            with self._transaction():
                if regenerate:
                    self._delete_waste_recommendations_for_run(analysis_run_id)
                recommendations = tuple(
                    self._create_recommendation(organization_id, payload)
                    for payload in rec_payloads
                )
                metadata["ai_insights"] = ai_insights
                metadata["pipeline_timeline"] = timeline.to_list()
                updated = self._analyses.update(run, {"runtime_metadata": metadata})
            trace.mark("persistence_completed")
        except Exception as exc:
            category = classify_exception(exc)
            timeline.fail_stage(PipelineStage.AI_COMPLETED, exc)
            metadata["pipeline_timeline"] = timeline.to_list()
            self._analyses.update(run, {"runtime_metadata": metadata})
            log_pipeline_event(
                logger,
                "pipeline_stage",
                level=logging.WARNING,
                stage=PipelineStage.AI_COMPLETED.value,
                status="failed",
                organization_id=str(organization_id),
                analysis_run_id=str(analysis_run_id),
                error_category=category,
                message=str(exc),
            )
            raise

        log_pipeline_event(
            logger,
            "pipeline_stage",
            stage=PipelineStage.AI_COMPLETED.value,
            status="completed",
            organization_id=str(organization_id),
            analysis_run_id=str(analysis_run_id),
            duration_ms=round((time.perf_counter() - pipeline_started) * 1000, 2),
        )
        trace.mark("service_completed")

        try_materialize(
            self._notifications,
            initiating_user_id,
            lambda: self._notifications.materialize_ai_recommendations_completion(
                organization_id,
                analysis_run_id,
                initiating_user_id=initiating_user_id,
                recommendation_count=len(recommendations),
            ),
        )

        return AiRecommendationOutcome(
            analysis_run=updated,
            facts_contract=facts,
            recommendations=recommendations,
            ai_insights=ai_insights,
        )

    def generate_risk_recommendations(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        regenerate: bool = False,
        initiating_user_id: uuid.UUID | None = None,
    ) -> AiRecommendationOutcome:
        """Generate risk-domain AI narratives and mitigation recommendations."""
        if self._risk_analysis is None:
            raise AiRecommendationError(
                "risk_ai_unavailable",
                "Risk analysis repository is not configured",
            )

        run = self._analyses.get(analysis_run_id)
        if run is None:
            raise ResourceNotFoundError("AnalysisRun", analysis_run_id)
        self._check_ownership(run, "AnalysisRun", organization_id)
        self._validate_risk_run_preconditions(run)
        prompt_language = self._resolve_prompt_language(organization_id)

        metadata = dict(run.runtime_metadata or {})
        existing_insights = metadata.get("ai_insights")
        if existing_insights and not regenerate:
            raise AiRecommendationError(
                "ai_insights_already_exist",
                "Risk AI insights already exist for this analysis run; "
                "pass regenerate=true to replace",
            )

        timeline = PipelineTimeline(
            organization_id=str(organization_id),
            file_id=str(run.source_file_id) if run.source_file_id else None,
            snapshot_id=str(run.source_snapshot_id) if run.source_snapshot_id else None,
            analysis_run_id=str(analysis_run_id),
            inherited=load_pipeline_timeline(metadata),
        )
        pipeline_started = time.perf_counter()
        trace = begin_trace(str(analysis_run_id), "risk")
        timeline.start_stage(PipelineStage.AI_STARTED)
        log_pipeline_event(
            logger,
            "pipeline_stage",
            stage=PipelineStage.AI_STARTED.value,
            status="started",
            organization_id=str(organization_id),
            analysis_run_id=str(analysis_run_id),
            domain="risk",
        )

        try:
            facts = load_risk_facts_contract(metadata)
            supplement = build_risk_metadata_supplement(metadata)
            trace.mark(
                "preflight_completed",
                detail=f"parallel={settings.ai.parallel_tasks_enabled} provider={settings.ai.ai_provider}",
            )
            try:
                task_results = self._execute_risk_tasks(
                    facts,
                    prompt_language=prompt_language,
                    prompt_supplement=supplement,
                )
            except (AIConnectionError, AITimeoutError):
                generated_at = datetime.now(timezone.utc)
                ai_insights = facts_only_insights_payload(
                    facts=facts,
                    model_name=self._model_name,
                    domain="risk",
                    narrative_status=NARRATIVE_LLM_UNAVAILABLE,
                    generated_at_iso=generated_at.isoformat(),
                )
                timeline.complete_stage(PipelineStage.AI_COMPLETED)
                with self._transaction():
                    metadata["ai_insights"] = ai_insights
                    metadata["pipeline_timeline"] = timeline.to_list()
                    updated = self._analyses.update(run, {"runtime_metadata": metadata})
                return AiRecommendationOutcome(
                    analysis_run=updated,
                    facts_contract=facts,
                    recommendations=(),
                    ai_insights=ai_insights,
                )

            trace.mark("llm_tasks_completed", detail=f"count={len(task_results)}")
            validate_risk_task_results(task_results)
            generated_at = datetime.now(timezone.utc)

            exec_task = next(
                r for r in task_results if r.task == PromptTask.RISK_EXECUTIVE_SUMMARY
            )
            guarded_exec, exec_status = guard_executive_summary_task(
                exec_task,
                facts,
                self._pipeline,
                domain="risk",
                prompt_language=prompt_language,
                prompt_supplement=supplement,
            )
            task_results = merge_task_results(task_results, guarded_exec)

            rec_task = next(
                r for r in task_results if r.task == RISK_RECOMMENDATION_TASK
            )
            traceability = self._build_risk_traceability(run, metadata)
            rec_payloads, rec_status = parse_and_map_risk_recommendations(
                rec_task,
                facts,
                analysis_run_id,
                self._model_name,
                traceability,
                pipeline=self._pipeline,
                prompt_language=prompt_language,
                prompt_supplement=supplement,
            )
            snapshot_id = str(run.source_snapshot_id) if run.source_snapshot_id else None
            narrative_status = exec_status or rec_status
            ai_insights = build_risk_ai_insights_payload(
                task_results=task_results,
                facts_contract=facts,
                model_name=self._model_name,
                traceability=traceability,
                source_snapshot_id=snapshot_id,
                generated_at=generated_at,
                narrative_status=narrative_status,
                omit_executive_summary=exec_status is not None,
            )

            timeline.complete_stage(PipelineStage.AI_COMPLETED)
            with self._transaction():
                if regenerate:
                    self._delete_risk_recommendations_for_run(analysis_run_id)
                recommendations = tuple(
                    self._create_recommendation(organization_id, payload)
                    for payload in rec_payloads
                )
                metadata["ai_insights"] = ai_insights
                metadata["pipeline_timeline"] = timeline.to_list()
                updated = self._analyses.update(run, {"runtime_metadata": metadata})
        except Exception as exc:
            category = classify_exception(exc)
            timeline.fail_stage(PipelineStage.AI_COMPLETED, exc)
            metadata["pipeline_timeline"] = timeline.to_list()
            self._analyses.update(run, {"runtime_metadata": metadata})
            log_pipeline_event(
                logger,
                "pipeline_stage",
                level=logging.WARNING,
                stage=PipelineStage.AI_COMPLETED.value,
                status="failed",
                organization_id=str(organization_id),
                analysis_run_id=str(analysis_run_id),
                domain="risk",
                error_category=category,
                message=str(exc),
            )
            raise

        log_pipeline_event(
            logger,
            "pipeline_stage",
            stage=PipelineStage.AI_COMPLETED.value,
            status="completed",
            organization_id=str(organization_id),
            analysis_run_id=str(analysis_run_id),
            domain="risk",
            duration_ms=round((time.perf_counter() - pipeline_started) * 1000, 2),
            recommendation_count=len(recommendations),
        )
        trace.mark("service_completed")

        try_materialize(
            self._notifications,
            initiating_user_id,
            lambda: self._notifications.materialize_risk_ai_recommendations_completion(
                organization_id,
                analysis_run_id,
                initiating_user_id=initiating_user_id,
                recommendation_count=len(recommendations),
            ),
        )

        return AiRecommendationOutcome(
            analysis_run=updated,
            facts_contract=facts,
            recommendations=recommendations,
            ai_insights=ai_insights,
        )

    def _validate_risk_run_preconditions(self, run: AnalysisRun) -> None:
        if run.analysis_type != AnalysisType.RISK:
            raise InvalidStateError(
                f"Analysis run type must be '{AnalysisType.RISK.value}' "
                f"(got '{run.analysis_type}')"
            )
        if run.status != AnalysisRunStatus.COMPLETED:
            raise InvalidStateError(
                f"Analysis run must be completed (current status: '{run.status}')"
            )
        result = self._risk_analysis.get_result_for_run(run.id)
        if result is None:
            raise InvalidStateError(
                "Analysis run has no risk_analysis_results Gold record"
            )

    def _execute_risk_tasks(
        self,
        facts_contract: FactsContract,
        *,
        prompt_language: str,
        prompt_supplement: str,
    ) -> tuple[TaskExecutionResult, ...]:
        return self._pipeline.execute_tasks(
            facts_contract,
            RISK_TASK_EXECUTION_ORDER,
            domain="risk",
            prompt_language=prompt_language,
            prompt_supplement=prompt_supplement,
            parallel=settings.ai.parallel_tasks_enabled,
        )

    def _build_risk_traceability(
        self, run: AnalysisRun, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        result = self._risk_analysis.get_result_for_run(run.id)
        findings = self._risk_analysis.list_findings(run.id)
        finding_ids = [str(item.id) for item in findings]
        if not finding_ids:
            raw_findings = metadata.get("risk_findings") or []
            if isinstance(raw_findings, list):
                finding_ids = [
                    str(item.get("finding_id"))
                    for item in raw_findings
                    if isinstance(item, dict) and item.get("finding_id")
                ]
        promoted_risk_ids = [
            str(item.promoted_risk_id)
            for item in findings
            if item.promoted_risk_id is not None
        ]
        return {
            "analysis_run_id": str(run.id),
            "risk_analysis_result_id": str(result.id) if result is not None else None,
            "source_snapshot_id": (
                str(result.source_snapshot_id)
                if result is not None and result.source_snapshot_id
                else (
                    str(run.source_snapshot_id) if run.source_snapshot_id else None
                )
            ),
            "finding_ids": finding_ids,
            "promoted_risk_ids": promoted_risk_ids,
        }

    def _delete_risk_recommendations_for_run(
        self, analysis_run_id: uuid.UUID
    ) -> None:
        existing = self._recommendation_repo.list_for_analysis_run(analysis_run_id)
        for rec in existing:
            if rec.domain_source == RecommendationDomain.RISK:
                self._recommendation_repo.delete(rec)

    def _validate_run_preconditions(self, run: AnalysisRun) -> None:
        if run.analysis_type != AnalysisType.FINANCIAL_WASTE:
            raise InvalidStateError(
                f"Analysis run type must be '{AnalysisType.FINANCIAL_WASTE.value}' "
                f"(got '{run.analysis_type}')"
            )
        if run.status != AnalysisRunStatus.COMPLETED:
            raise InvalidStateError(
                f"Analysis run must be completed (current status: '{run.status}')"
            )
        waste_result = self._waste.get_result_for_run(run.id)
        if waste_result is None:
            raise InvalidStateError(
                "Analysis run has no waste_analysis_results Gold record"
            )

    def _resolve_prompt_language(self, organization_id: uuid.UUID) -> str:
        if self._settings is None:
            return settings.ai.default_prompt_language
        resolved = self._settings.get_resolved_settings(organization_id)
        if not resolved.ai_configuration.ai_recommendations_enabled:
            raise AiRecommendationsDisabledError()
        return resolved.localization.prompt_language

    def _execute_tasks(
        self,
        facts_contract: FactsContract,
        *,
        prompt_language: str,
        prompt_supplement: str | None = None,
    ) -> tuple[TaskExecutionResult, ...]:
        return self._pipeline.execute_tasks(
            facts_contract,
            TASK_EXECUTION_ORDER,
            domain="waste",
            prompt_language=prompt_language,
            prompt_supplement=prompt_supplement,
            parallel=settings.ai.parallel_tasks_enabled,
        )

    def _create_recommendation(
        self,
        organization_id: uuid.UUID,
        payload: dict[str, Any],
    ) -> Recommendation:
        recommendation = Recommendation(
            organization_id=organization_id,
            domain_source=payload["domain_source"],
            title=payload["title"],
            description=payload["description"],
            priority=payload["priority"],
            analysis_run_id=payload["analysis_run_id"],
            source_context=payload["source_context"],
        )
        return self._recommendation_repo.create(recommendation)

    def _delete_waste_recommendations_for_run(
        self, analysis_run_id: uuid.UUID
    ) -> None:
        existing = self._recommendation_repo.list_for_analysis_run(analysis_run_id)
        for rec in existing:
            if rec.domain_source == RecommendationDomain.WASTE:
                self._recommendation_repo.delete(rec)
