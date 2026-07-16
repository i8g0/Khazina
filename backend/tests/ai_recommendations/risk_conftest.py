"""Shared fixtures for risk AI recommendation tests."""

from __future__ import annotations

from app.ai.prompts.tasks import PromptTask
from app.ai_recommendations.risk_constants import RISK_TASK_EXECUTION_ORDER
from app.business.engines.risk import RiskEngine
from tests.business.risk_conftest import sample_risk_input


def sample_risk_facts_contract():
    return RiskEngine().run(sample_risk_input()).facts_contract


def sample_risk_runtime_metadata() -> dict:
    output = RiskEngine().run(sample_risk_input())
    from app.decision.mappers.risk_metadata import RiskMetadataMapper

    return {
        "facts_contract": output.facts_contract.to_dict(),
        **RiskMetadataMapper.to_success_metadata(output),
    }


def sample_risk_mitigation_text() -> str:
    return (
        "1.\n"
        "الفئة: إجراءات فورية\n"
        "الإجراء المقترح: مراجعة السيولة فوراً\n"
        "المبرر: نتيجة سيولة عالية الأولوية\n"
        "الحقائق المرجعية: risk.liquidity_ratio\n\n"
        "2.\n"
        "الفئة: إجراءات المراقبة\n"
        "الإجراء المقترح: متابعة أسبوعية للتدفقات\n"
        "المبرر: مراقبة مستمرة\n"
        "الحقائق المرجعية: risk.total_findings\n\n"
        "3.\n"
        "الفئة: ضوابط مالية\n"
        "الإجراء المقترح: تشديد موافقات الصرف\n"
        "المبرر: ضبط مالي\n"
        "الحقائق المرجعية: risk.waste_percentage\n\n"
        "4.\n"
        "الفئة: ضوابط تشغيلية\n"
        "الإجراء المقترح: مراجعة العقود المتداخلة\n"
        "المبرر: تقليل التعرض التشغيلي\n"
        "الحقائق المرجعية: risk.top_category\n\n"
        "5.\n"
        "الفئة: حوكمة\n"
        "الإجراء المقترح: إحالة للجنة المخاطر\n"
        "المبرر: حوكمة تنفيذية\n"
        "الحقائق المرجعية: risk.overall_posture_level"
    )


class MockRiskOllamaByTask:
    def __init__(
        self,
        *,
        mitigation_text: str | None = None,
    ) -> None:
        self._responses = {
            PromptTask.RISK_EXECUTIVE_SUMMARY: "ملخص تنفيذي للمخاطر المالية.",
            PromptTask.RISK_EXECUTIVE_BRIEF: "موجز تنفيذي: وضع المخاطر يتطلب انتباهاً.",
            PromptTask.RISK_EXPLANATION: "شرح: تم رصد مخاطر بناءً على الحقائق الحتمية.",
            PromptTask.RISK_MITIGATION_OPTIONS: mitigation_text
            or sample_risk_mitigation_text(),
            PromptTask.RISK_BOARD_REPORT: "تقرير مجلس: 3 نقاط للنقاش.",
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
        if self._call_index < len(RISK_TASK_EXECUTION_ORDER):
            task = RISK_TASK_EXECUTION_ORDER[self._call_index]
            self._call_index += 1
        else:
            task = self.calls[-1]
        self.calls.append(task)
        return self._responses[task]
