"""Validate AI task outputs before persistence (§11.6)."""

from __future__ import annotations

from app.ai.prompts.tasks import PromptTask
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.pipeline import TaskExecutionResult


def validate_task_results(task_results: tuple[TaskExecutionResult, ...]) -> None:
    for result in task_results:
        text = result.parsed_response.text.strip()
        if result.task == PromptTask.EXECUTIVE_SUMMARY and not text:
            raise AiRecommendationError(
                "missing_executive_summary",
                "Executive summary text is empty",
            )
        if result.task == PromptTask.RISK_ANALYSIS and not text:
            raise AiRecommendationError(
                "missing_risk_explanation",
                "Risk explanation text is empty",
            )
        if result.task == PromptTask.RECOMMENDATIONS and not text:
            raise AiRecommendationError(
                "invalid_recommendation_count",
                "Recommendations text is empty",
            )
