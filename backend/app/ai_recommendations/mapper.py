"""Map AI task outputs to insights artifacts and recommendation payloads (§11)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.ai.prompts.tasks import PromptTask
from app.ai.prompts.version import PROMPT_VERSION
from app.ai_recommendations.constants import NARRATIVE_KEY_BY_TASK
from app.ai_recommendations.evidence_validator import validate_waste_recommendations
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.pipeline import AiTaskPipeline, TaskExecutionResult
from app.core.config import settings
from app.presentation.evidence_registry import EvidenceRegistry
from app.presentation.narrative_guard import (
    NARRATIVE_REJECTED,
    guard_retry_addendum,
    retry_task_with_addendum,
)
from app.ai_recommendations.recommendation_parser import (
    ParsedRecommendationItem,
    parse_recommendations_text,
)
from app.business.facts.contract import FactsContract
from app.db.models.enums import RecommendationDomain, RecommendationPriority
from app.presentation.executive_sanitize import sanitize_executive_text


def build_ai_insights_payload(
    *,
    task_results: tuple[TaskExecutionResult, ...],
    facts_contract: FactsContract,
    model_name: str,
    source_snapshot_id: str | None,
    generated_at: datetime | None = None,
    narrative_status: str | None = None,
    omit_executive_summary: bool = False,
) -> dict[str, Any]:
    ts = generated_at or datetime.now(timezone.utc)
    narrative: dict[str, Any] = {}
    executive_summary: str | None = None
    risk_explanation: str | None = None

    for result in task_results:
        key = NARRATIVE_KEY_BY_TASK[result.task]
        narrative[key] = _narrative_entry(result, model_name, ts)
        if result.task == PromptTask.EXECUTIVE_SUMMARY and not omit_executive_summary:
            executive_summary = sanitize_executive_text(result.parsed_response.text)
        elif result.task == PromptTask.RISK_ANALYSIS:
            risk_explanation = sanitize_executive_text(result.parsed_response.text)

    if not omit_executive_summary and (not executive_summary or not risk_explanation):
        raise AiRecommendationError(
            "incomplete_ai_insights",
            "Executive summary and risk explanation are required",
        )

    payload: dict[str, Any] = {
        "generated_at": ts.isoformat(),
        "prompt_version": PROMPT_VERSION,
        "model": model_name,
        "tasks_executed": [r.task.value for r in task_results],
        "facts_contract_version": facts_contract.contract_version,
        "engine_id": facts_contract.engine_id,
        "engine_version": facts_contract.engine_version,
        "risk_explanation": risk_explanation or "",
        "narrative": narrative,
    }
    if not omit_executive_summary:
        payload["executive_summary"] = executive_summary
    if narrative_status:
        payload["narrative_status"] = narrative_status
    if source_snapshot_id is not None:
        payload["source_snapshot_id"] = source_snapshot_id
    return payload


def map_recommendation_payloads(
    *,
    items: tuple[ParsedRecommendationItem, ...],
    facts_contract: FactsContract,
    analysis_run_id: uuid.UUID,
    task_result: TaskExecutionResult,
    model_name: str,
    generated_at: datetime | None = None,
) -> list[dict[str, Any]]:
    ts = generated_at or datetime.now(timezone.utc)
    payloads: list[dict[str, Any]] = []
    for item in items:
        priority = _to_recommendation_priority(item.priority)
        executive_ctx = item.executive.to_dict() if item.executive else None
        payload: dict[str, Any] = {
            "title": sanitize_executive_text(item.title),
            "description": sanitize_executive_text(item.description),
            "priority": priority.value,
            "domain_source": RecommendationDomain.WASTE.value,
            "analysis_run_id": analysis_run_id,
            "source_context": {
                "task": PromptTask.RECOMMENDATIONS.value,
                "prompt_task": PromptTask.RECOMMENDATIONS.value,
                "parsed_format": task_result.parsed_response.format,
                "model": model_name,
                "prompt_version": task_result.composed_prompt.prompt_version,
                "prompt_language": task_result.composed_prompt.prompt_language,
                "generated_at": ts.isoformat(),
                "item_index": item.index,
                "facts_contract_version": facts_contract.contract_version,
                "engine_id": facts_contract.engine_id,
                "executive": executive_ctx,
            },
        }
        payloads.append(payload)
    return payloads


def parse_and_map_recommendations(
    task_result: TaskExecutionResult,
    facts_contract: FactsContract,
    analysis_run_id: uuid.UUID,
    model_name: str,
    *,
    pipeline: AiTaskPipeline | None = None,
    prompt_language: str | None = None,
    prompt_supplement: str | None = None,
) -> tuple[list[dict[str, Any]], str | None]:
    items, narrative_status = _parse_recommendations_with_guard(
        task_result,
        facts_contract,
        pipeline=pipeline,
        prompt_language=prompt_language,
        prompt_supplement=prompt_supplement,
    )
    if narrative_status:
        return [], narrative_status
    return map_recommendation_payloads(
        items=items,
        facts_contract=facts_contract,
        analysis_run_id=analysis_run_id,
        task_result=task_result,
        model_name=model_name,
    ), None


def _parse_recommendations_with_guard(
    task_result: TaskExecutionResult,
    facts_contract: FactsContract,
    *,
    pipeline: AiTaskPipeline | None = None,
    prompt_language: str | None = None,
    prompt_supplement: str | None = None,
) -> tuple[tuple[ParsedRecommendationItem, ...], str | None]:
    items = parse_recommendations_text(task_result.parsed_response.text)
    errors = _waste_recommendation_errors(items, facts_contract)
    if not errors:
        return items, None

    if pipeline is not None and settings.ai.guard_max_retries > 0:
        retried = retry_task_with_addendum(
            pipeline,
            facts_contract,
            task_result.task,
            guard_retry_addendum(errors),
            prompt_language=prompt_language,
            prompt_supplement=prompt_supplement,
        )
        items = parse_recommendations_text(retried.parsed_response.text)
        retry_errors = _waste_recommendation_errors(items, facts_contract)
        if not retry_errors:
            return items, None
        return (), NARRATIVE_REJECTED

    validate_waste_recommendations(items, facts_contract)
    return items, None


def _waste_recommendation_errors(
    items: tuple[ParsedRecommendationItem, ...],
    facts_contract: FactsContract,
) -> list[str]:
    registry = EvidenceRegistry.from_contract(facts_contract)
    errors: list[str] = []
    for item in items:
        combined = f"{item.title}\n{item.description}"
        if item.executive:
            combined = f"{combined}\n{item.executive.to_description()}"
        item_errors = registry.validate_text(combined)
        if item.executive and not item.executive.evidence:
            item_errors.append("missing_evidence_section")
        errors.extend(item_errors)
    return errors


def _narrative_entry(
    result: TaskExecutionResult,
    model_name: str,
    generated_at: datetime,
) -> dict[str, Any]:
    return {
        "task": result.task.value,
        "format": result.parsed_response.format,
        "text": sanitize_executive_text(result.parsed_response.text),
        "data": result.parsed_response.data,
        "model": model_name,
        "prompt_version": result.composed_prompt.prompt_version,
        "prompt_language": result.composed_prompt.prompt_language,
        "generated_at": generated_at.isoformat(),
    }


def _to_recommendation_priority(priority: str) -> RecommendationPriority:
    if priority == "high":
        return RecommendationPriority.HIGH
    if priority == "low":
        return RecommendationPriority.LOW
    return RecommendationPriority.MEDIUM
