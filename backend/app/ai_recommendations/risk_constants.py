"""Sprint 9.5 Risk-domain AI constants."""

from __future__ import annotations

from app.ai.prompts.tasks import PromptTask

RISK_TASK_EXECUTION_ORDER: tuple[PromptTask, ...] = (
    PromptTask.RISK_EXECUTIVE_SUMMARY,
    PromptTask.RISK_EXECUTIVE_BRIEF,
    PromptTask.RISK_EXPLANATION,
    PromptTask.RISK_MITIGATION_OPTIONS,
    PromptTask.RISK_BOARD_REPORT,
)

RISK_NARRATIVE_KEY_BY_TASK: dict[PromptTask, str] = {
    PromptTask.RISK_EXECUTIVE_SUMMARY: "risk_executive_summary",
    PromptTask.RISK_EXECUTIVE_BRIEF: "risk_executive_brief",
    PromptTask.RISK_EXPLANATION: "risk_explanation",
    PromptTask.RISK_MITIGATION_OPTIONS: "risk_mitigation_options",
    PromptTask.RISK_BOARD_REPORT: "risk_board_report",
}

RISK_RECOMMENDATION_TASK = PromptTask.RISK_MITIGATION_OPTIONS

MIN_RISK_RECOMMENDATION_ITEMS = 3
MAX_RISK_RECOMMENDATION_ITEMS = 8

RISK_RECOMMENDATION_CATEGORIES: tuple[str, ...] = (
    "immediate_action",
    "monitoring_action",
    "financial_control",
    "operational_control",
    "governance",
    "compliance",
)

CATEGORY_LABEL_TO_CODE: dict[str, str] = {
    "إجراءات فورية": "immediate_action",
    "إجراءات المراقبة": "monitoring_action",
    "ضوابط مالية": "financial_control",
    "ضوابط تشغيلية": "operational_control",
    "حوكمة": "governance",
    "امتثال": "compliance",
}
