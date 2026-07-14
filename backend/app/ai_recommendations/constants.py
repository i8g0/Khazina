"""Sprint 6.4 AI Recommendation constants."""

from __future__ import annotations

from app.ai.prompts.tasks import PromptTask

TASK_EXECUTION_ORDER: tuple[PromptTask, ...] = (
    PromptTask.EXECUTIVE_SUMMARY,
    PromptTask.RECOMMENDATIONS,
    PromptTask.RISK_ANALYSIS,
)

NARRATIVE_KEY_BY_TASK: dict[PromptTask, str] = {
    PromptTask.EXECUTIVE_SUMMARY: "executive_summary",
    PromptTask.RECOMMENDATIONS: "recommendations",
    PromptTask.RISK_ANALYSIS: "risk_analysis",
}

MIN_RECOMMENDATION_ITEMS = 3
MAX_RECOMMENDATION_ITEMS = 6
MAX_TITLE_LENGTH = 500

PRIORITY_HIGH_KEYWORDS = frozenset({"عالية", "عالي", "high"})
PRIORITY_MEDIUM_KEYWORDS = frozenset({"متوسطة", "متوسط", "medium"})
