"""Shared fixtures for AI recommendation tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.ai.prompts.tasks import PromptTask
from app.business.engines.waste.engine import WasteEngine
from app.business.engines.waste.input import WasteCategoryInput, WasteEngineInput
from app.business.facts.contract import FactsContract


def sample_waste_engine_input() -> WasteEngineInput:
    return WasteEngineInput(
        total_spend=50_000_000.0,
        total_waste_amount=2_340_000.0,
        categories=(
            WasteCategoryInput("overlapping_contracts", 745_000.0),
            WasteCategoryInput("operations", 520_000.0),
            WasteCategoryInput("finance", 1_075_000.0),
        ),
        organization_id="org-123",
        period="2026-Q2",
        generated_at=datetime(2026, 7, 13, tzinfo=UTC),
    )


def sample_facts_contract() -> FactsContract:
    return WasteEngine().run(sample_waste_engine_input())


def sample_recommendations_text() -> str:
    return (
        "1. مراجعة العقود المتداخلة فوراً — أولوية عالية\n"
        "2. تحسين عمليات المشتريات — أولوية متوسطة\n"
        "3. تقليل الهدر المالي في القسم المالي — أولوية عالية"
    )


class MockOllamaByTask:
    """Returns deterministic responses per call order (EXECUTIVE → RECOMMENDATIONS → RISK)."""

    _TASK_ORDER = (
        PromptTask.EXECUTIVE_SUMMARY,
        PromptTask.RECOMMENDATIONS,
        PromptTask.RISK_ANALYSIS,
    )

    def __init__(
        self,
        *,
        executive_summary: str = "ملخص تنفيذي للإدارة حول الهدر المالي.",
        recommendations: str | None = None,
        risk_analysis: str = "تحليل المخاطر: مستوى الهدر مرتفع ويتطلب تدخل فوري.",
    ) -> None:
        self._responses = {
            PromptTask.EXECUTIVE_SUMMARY: executive_summary,
            PromptTask.RECOMMENDATIONS: recommendations or sample_recommendations_text(),
            PromptTask.RISK_ANALYSIS: risk_analysis,
        }
        self.calls: list[PromptTask] = []
        self._call_index = 0

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        format_json: bool = False,
    ) -> str:
        task = self._TASK_ORDER[self._call_index]
        self._call_index += 1
        self.calls.append(task)
        return self._responses[task]
