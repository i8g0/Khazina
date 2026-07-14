"""Map AI task outputs to insights artifacts and recommendation payloads (§11)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.ai.prompts.tasks import PromptTask
from app.ai.prompts.version import PROMPT_VERSION
from app.ai_recommendations.constants import NARRATIVE_KEY_BY_TASK
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.pipeline import TaskExecutionResult
from app.ai_recommendations.recommendation_parser import (
    ParsedRecommendationItem,
    parse_recommendations_text,
)
from app.business.facts.contract import FactsContract
from app.db.models.enums import RecommendationDomain, RecommendationPriority


def build_ai_insights_payload(
    *,
    task_results: tuple[TaskExecutionResult, ...],
    facts_contract: FactsContract,
    model_name: str,
    source_snapshot_id: str | None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    ts = generated_at or datetime.now(timezone.utc)
    narrative: dict[str, Any] = {}
    executive_summary: str | None = None
    risk_explanation: str | None = None

    for result in task_results:
        key = NARRATIVE_KEY_BY_TASK[result.task]
        narrative[key] = _narrative_entry(result, model_name, ts)
        if result.task == PromptTask.EXECUTIVE_SUMMARY:
            executive_summary = result.parsed_response.text
        elif result.task == PromptTask.RISK_ANALYSIS:
            risk_explanation = result.parsed_response.text

    if not executive_summary or not risk_explanation:
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
        "executive_summary": executive_summary,
        "risk_explanation": risk_explanation,
        "narrative": narrative,
    }
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
        payload: dict[str, Any] = {
            "title": item.title,
            "description": item.description,
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
            },
        }
        payloads.append(payload)
    return payloads


def parse_and_map_recommendations(
    task_result: TaskExecutionResult,
    facts_contract: FactsContract,
    analysis_run_id: uuid.UUID,
    model_name: str,
) -> list[dict[str, Any]]:
    items = parse_recommendations_text(task_result.parsed_response.text)
    return map_recommendation_payloads(
        items=items,
        facts_contract=facts_contract,
        analysis_run_id=analysis_run_id,
        task_result=task_result,
        model_name=model_name,
    )


def _narrative_entry(
    result: TaskExecutionResult,
    model_name: str,
    generated_at: datetime,
) -> dict[str, Any]:
    return {
        "task": result.task.value,
        "format": result.parsed_response.format,
        "text": result.parsed_response.text,
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
