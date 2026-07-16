"""Map Risk AI task outputs to insights and recommendation payloads (Sprint 9.5)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.ai.prompts.tasks import PromptTask
from app.ai.prompts.version import PROMPT_VERSION
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.mapper import _narrative_entry
from app.ai_recommendations.pipeline import TaskExecutionResult
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


def build_risk_ai_insights_payload(
    *,
    task_results: tuple[TaskExecutionResult, ...],
    facts_contract: FactsContract,
    model_name: str,
    traceability: dict[str, Any],
    source_snapshot_id: str | None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    ts = generated_at or datetime.now(timezone.utc)
    narrative: dict[str, Any] = {}
    summaries: dict[str, str] = {}

    for result in task_results:
        key = RISK_NARRATIVE_KEY_BY_TASK[result.task]
        narrative[key] = _narrative_entry(result, model_name, ts)
        summaries[key] = result.parsed_response.text.strip()

    required = (
        PromptTask.RISK_EXECUTIVE_SUMMARY,
        PromptTask.RISK_EXPLANATION,
        PromptTask.RISK_MITIGATION_OPTIONS,
    )
    for task in required:
        text = summaries.get(RISK_NARRATIVE_KEY_BY_TASK[task], "")
        if not text:
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
                "title": item.title,
                "description": item.description,
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
) -> list[dict[str, Any]]:
    items = parse_risk_mitigation_text(task_result.parsed_response.text)
    return map_risk_recommendation_payloads(
        items=items,
        facts_contract=facts_contract,
        analysis_run_id=analysis_run_id,
        task_result=task_result,
        model_name=model_name,
        traceability=traceability,
    )


def _to_recommendation_priority(priority: str) -> RecommendationPriority:
    if priority == "high":
        return RecommendationPriority.HIGH
    if priority == "low":
        return RecommendationPriority.LOW
    return RecommendationPriority.MEDIUM
