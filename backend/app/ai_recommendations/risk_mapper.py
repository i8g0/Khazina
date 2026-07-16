"""Map Risk AI task outputs to insights and recommendation payloads (Sprint 9.5)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.ai.prompts.tasks import PromptTask
from app.ai.prompts.version import PROMPT_VERSION
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.risk_evidence_validator import validate_risk_recommendations
from app.ai_recommendations.mapper import _narrative_entry
from app.ai_recommendations.pipeline import AiTaskPipeline, TaskExecutionResult
from app.core.config import settings
from app.presentation.evidence_registry import EvidenceRegistry
from app.presentation.narrative_guard import (
    NARRATIVE_REJECTED,
    guard_retry_addendum,
    retry_task_with_addendum,
)
from app.ai_recommendations.risk_constants import (
    RISK_NARRATIVE_KEY_BY_TASK,
    RISK_RECOMMENDATION_TASK,
)
from app.ai_recommendations.risk_recommendation_parser import (
    ParsedRiskRecommendationItem,
    parse_risk_mitigation_text,
)
from app.business.facts.contract import FactsContract
from app.db.models.enums import RecommendationDomain, RecommendationPriority
from app.presentation.executive_sanitize import sanitize_executive_text


def build_risk_ai_insights_payload(
    *,
    task_results: tuple[TaskExecutionResult, ...],
    facts_contract: FactsContract,
    model_name: str,
    traceability: dict[str, Any],
    source_snapshot_id: str | None,
    generated_at: datetime | None = None,
    narrative_status: str | None = None,
    omit_executive_summary: bool = False,
) -> dict[str, Any]:
    ts = generated_at or datetime.now(timezone.utc)
    narrative: dict[str, Any] = {}
    summaries: dict[str, str] = {}

    for result in task_results:
        key = RISK_NARRATIVE_KEY_BY_TASK[result.task]
        narrative[key] = _narrative_entry(result, model_name, ts)
        if result.task == PromptTask.RISK_EXECUTIVE_SUMMARY and not omit_executive_summary:
            summaries[key] = sanitize_executive_text(result.parsed_response.text.strip())
        elif result.task != PromptTask.RISK_EXECUTIVE_SUMMARY:
            summaries[key] = sanitize_executive_text(result.parsed_response.text.strip())

    required = (
        PromptTask.RISK_EXPLANATION,
        PromptTask.RISK_MITIGATION_OPTIONS,
    )
    if not omit_executive_summary:
        required = (PromptTask.RISK_EXECUTIVE_SUMMARY, *required)
    for task in required:
        text = summaries.get(RISK_NARRATIVE_KEY_BY_TASK[task], "")
        if not text and task != PromptTask.RISK_MITIGATION_OPTIONS:
            raise AiRecommendationError(
                "incomplete_ai_insights",
                f"Required risk AI narrative missing for task '{task.value}'",
            )

    payload: dict[str, Any] = {
        "domain": "risk",
        "generated_at": ts.isoformat(),
        "prompt_version": PROMPT_VERSION,
        "model": model_name,
        "tasks_executed": [r.task.value for r in task_results],
        "facts_contract_version": facts_contract.contract_version,
        "engine_id": facts_contract.engine_id,
        "engine_version": facts_contract.engine_version,
        "narrative": narrative,
        "traceability": traceability,
        **summaries,
    }
    if narrative_status:
        payload["narrative_status"] = narrative_status
    if source_snapshot_id is not None:
        payload["source_snapshot_id"] = source_snapshot_id
    return payload


def map_risk_recommendation_payloads(
    *,
    items: tuple[ParsedRiskRecommendationItem, ...],
    facts_contract: FactsContract,
    analysis_run_id: uuid.UUID,
    task_result: TaskExecutionResult,
    model_name: str,
    traceability: dict[str, Any],
    generated_at: datetime | None = None,
) -> list[dict[str, Any]]:
    ts = generated_at or datetime.now(timezone.utc)
    payloads: list[dict[str, Any]] = []
    for item in items:
        priority = _to_recommendation_priority(item.priority)
        payloads.append(
            {
                "title": sanitize_executive_text(item.title),
                "description": sanitize_executive_text(item.description),
                "priority": priority.value,
                "domain_source": RecommendationDomain.RISK.value,
                "analysis_run_id": analysis_run_id,
                "source_context": {
                    "task": RISK_RECOMMENDATION_TASK.value,
                    "prompt_task": RISK_RECOMMENDATION_TASK.value,
                    "parsed_format": task_result.parsed_response.format,
                    "model": model_name,
                    "prompt_version": task_result.composed_prompt.prompt_version,
                    "prompt_language": task_result.composed_prompt.prompt_language,
                    "generated_at": ts.isoformat(),
                    "item_index": item.index,
                    "recommendation_category": item.category_code,
                    "facts_contract_version": facts_contract.contract_version,
                    "engine_id": facts_contract.engine_id,
                    "traceability": traceability,
                    "deterministic_source": True,
                },
            }
        )
    return payloads


def parse_and_map_risk_recommendations(
    task_result: TaskExecutionResult,
    facts_contract: FactsContract,
    analysis_run_id: uuid.UUID,
    model_name: str,
    traceability: dict[str, Any],
    *,
    pipeline: AiTaskPipeline | None = None,
    prompt_language: str | None = None,
    prompt_supplement: str | None = None,
) -> tuple[list[dict[str, Any]], str | None]:
    items, narrative_status = _parse_risk_recommendations_with_guard(
        task_result,
        facts_contract,
        pipeline=pipeline,
        prompt_language=prompt_language,
        prompt_supplement=prompt_supplement,
    )
    if narrative_status:
        return [], narrative_status
    return map_risk_recommendation_payloads(
        items=items,
        facts_contract=facts_contract,
        analysis_run_id=analysis_run_id,
        task_result=task_result,
        model_name=model_name,
        traceability=traceability,
    ), None


def _parse_risk_recommendations_with_guard(
    task_result: TaskExecutionResult,
    facts_contract: FactsContract,
    *,
    pipeline: AiTaskPipeline | None = None,
    prompt_language: str | None = None,
    prompt_supplement: str | None = None,
) -> tuple[tuple[ParsedRiskRecommendationItem, ...], str | None]:
    items = parse_risk_mitigation_text(task_result.parsed_response.text)
    errors = _risk_recommendation_errors(items, facts_contract)
    if not errors:
        return items, None

    if pipeline is not None and settings.ai.guard_max_retries > 0:
        retried = retry_task_with_addendum(
            pipeline,
            facts_contract,
            task_result.task,
            guard_retry_addendum(errors),
            domain="risk",
            prompt_language=prompt_language,
            prompt_supplement=prompt_supplement,
        )
        items = parse_risk_mitigation_text(retried.parsed_response.text)
        retry_errors = _risk_recommendation_errors(items, facts_contract)
        if not retry_errors:
            return items, None
        return (), NARRATIVE_REJECTED

    validate_risk_recommendations(items, facts_contract)
    return items, None


def _risk_recommendation_errors(
    items: tuple[ParsedRiskRecommendationItem, ...],
    facts_contract: FactsContract,
) -> list[str]:
    registry = EvidenceRegistry.from_contract(facts_contract)
    errors: list[str] = []
    for item in items:
        combined = f"{item.title}\n{item.description}"
        errors.extend(registry.validate_risk_text(combined))
    return errors


def _to_recommendation_priority(priority: str) -> RecommendationPriority:
    if priority == "high":
        return RecommendationPriority.HIGH
    if priority == "low":
        return RecommendationPriority.LOW
    return RecommendationPriority.MEDIUM
