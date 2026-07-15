"""AI Recommendation Service — orchestrates Facts-only AI generation (Sprint 6.4)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.ai.client import OllamaClient
from app.ai.prompts.tasks import PromptTask
from app.ai_recommendations.constants import TASK_EXECUTION_ORDER
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.facts_loader import load_facts_contract
from app.ai_recommendations.mapper import (
    build_ai_insights_payload,
    parse_and_map_recommendations,
)
from app.ai_recommendations.pipeline import AiTaskPipeline, TaskExecutionResult
from app.ai_recommendations.validator import validate_task_results
from app.business.facts.contract import FactsContract
from app.core.config import settings
from app.db.models import AnalysisRun, Recommendation
from app.db.models.enums import AnalysisRunStatus, AnalysisType, RecommendationDomain
from app.repositories import AnalysisRepository, RecommendationRepository, WasteRepository
from app.services.base import BaseService
from app.services.exceptions import InvalidStateError, ResourceNotFoundError
from app.settings.exceptions import AiRecommendationsDisabledError
from app.settings.service import SettingsService


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
        task_pipeline: AiTaskPipeline | None = None,
        ollama_client: OllamaClient | None = None,
        settings_service: SettingsService | None = None,
    ) -> None:
        super().__init__(session)
        self._analyses = analysis_repository
        self._waste = waste_repository
        self._recommendation_repo = recommendation_repository
        self._model_name = settings.ai.ollama_model
        self._settings = settings_service
        client = ollama_client or OllamaClient(settings.ai)
        self._pipeline = task_pipeline or AiTaskPipeline(
            ollama_client=client,
            ollama_model=self._model_name,
            prompt_language=settings.ai.default_prompt_language,
        )

    def generate_waste_recommendations(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        regenerate: bool = False,
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

        facts = load_facts_contract(metadata)
        task_results = self._execute_tasks(facts, prompt_language=prompt_language)
        validate_task_results(task_results)
        generated_at = datetime.now(timezone.utc)

        rec_task = next(
            r for r in task_results if r.task == PromptTask.RECOMMENDATIONS
        )
        rec_payloads = parse_and_map_recommendations(
            rec_task,
            facts,
            analysis_run_id,
            self._model_name,
        )
        snapshot_id = str(run.source_snapshot_id) if run.source_snapshot_id else None
        ai_insights = build_ai_insights_payload(
            task_results=task_results,
            facts_contract=facts,
            model_name=self._model_name,
            source_snapshot_id=snapshot_id,
            generated_at=generated_at,
        )

        with self._transaction():
            if regenerate:
                self._delete_waste_recommendations_for_run(analysis_run_id)
            recommendations = tuple(
                self._create_recommendation(organization_id, payload)
                for payload in rec_payloads
            )
            metadata["ai_insights"] = ai_insights
            updated = self._analyses.update(run, {"runtime_metadata": metadata})

        return AiRecommendationOutcome(
            analysis_run=updated,
            facts_contract=facts,
            recommendations=recommendations,
            ai_insights=ai_insights,
        )

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
    ) -> tuple[TaskExecutionResult, ...]:
        results: list[TaskExecutionResult] = []
        for task in TASK_EXECUTION_ORDER:
            results.append(
                self._pipeline.execute_task(
                    facts_contract,
                    task,
                    domain="waste",
                    prompt_language=prompt_language,
                )
            )
        return tuple(results)

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
