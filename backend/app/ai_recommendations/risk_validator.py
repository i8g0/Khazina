"""Validate Risk-domain AI task outputs before persistence (Sprint 9.5)."""

from __future__ import annotations

from app.ai.prompts.tasks import PromptTask
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.pipeline import TaskExecutionResult
from app.ai_recommendations.risk_constants import RISK_NARRATIVE_KEY_BY_TASK


def validate_risk_task_results(task_results: tuple[TaskExecutionResult, ...]) -> None:
    seen = {result.task for result in task_results}
    for task in RISK_NARRATIVE_KEY_BY_TASK:
        if task not in seen:
            raise AiRecommendationError(
                "incomplete_ai_insights",
                f"Missing required risk AI task '{task.value}'",
            )

    for result in task_results:
        text = result.parsed_response.text.strip()
        if not text:
            raise AiRecommendationError(
                "empty_task_output",
                f"Risk AI task '{result.task.value}' returned empty text",
            )
        if result.task == PromptTask.RISK_MITIGATION_OPTIONS and len(text) < 20:
            raise AiRecommendationError(
                "invalid_recommendation_count",
                "Risk mitigation options output is too short",
            )
