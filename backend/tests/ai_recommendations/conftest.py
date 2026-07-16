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


def _executive_item(
    *,
    angle: str,
    problem: str,
    evidence: str,
    priority_rationale: str,
    impact: str,
    root_cause: str,
    decision: str,
    priority: str,
    owner: str,
    timeline: str,
    savings: str,
    kpi: str,
) -> str:
    return (
        f"الزاوية التنفيذية:\n{angle}\n"
        f"المشكلة:\n{problem}\n"
        f"الدليل:\n{evidence}\n"
        f"لماذا الأولوية:\n{priority_rationale}\n"
        f"السبب الجذري:\n{root_cause}\n"
        f"القرار:\n{decision}\n"
        f"الأثر على الأعمال:\n{impact}\n"
        f"الأولوية:\n{priority}\n"
        f"المسؤول:\n{owner}\n"
        f"الإطار الزمني:\n{timeline}\n"
        f"النتيجة المتوقعة:\n{savings}\n"
        f"مؤشر النجاح:\n{kpi}\n"
    )


def sample_recommendations_text() -> str:
    return (
        "1.\n"
        + _executive_item(
            angle="الحوكمة المالية",
            problem="تركز الهدر في الشؤون المالية خلال الربع الثاني 2026.",
            evidence=(
                "الفئة: الشؤون المالية\n"
                "مجال الأعمال: المالية والحوكمة\n"
                "الإدارة: الإدارة المالية\n"
                "الفترة: الربع الثاني 2026\n"
                "قيمة الهدر: 1,075,000 ريال\n"
                "النسبة: 45.9%\n"
                "الأثر المالي: 1,075,000 ريال"
            ),
            priority_rationale="الشؤون المالية تمثل 45.9% من الهدر — أكبر مصدر للخسارة.",
            impact="ضغط مباشر على الهامش التشغيلي.",
            root_cause="غير متوفر في البيانات — يتطلب تحليلاً تشغيلياً.",
            decision="إطلاق مراجعة حوكمة مالية مركّزة على اعتمادات الشؤون المالية.",
            priority="عالية",
            owner="الإدارة المالية",
            timeline="30–45 يوماً",
            savings="1,872,000 ريال ضمن الوفورات المحتملة.",
            kpi="خفض هدر الشؤون المالية 10% خلال 90 يوماً.",
        )
        + "2.\n"
        + _executive_item(
            angle="تحسين الموردين",
            problem="العقود المتداخلة تضيف طبقة ثانية من الهدر.",
            evidence=(
                "الفئة: العقود المتداخلة\n"
                "مجال الأعمال: إدارة العقود والمشتريات\n"
                "الإدارة: إدارة العقود\n"
                "الفترة: الربع الثاني 2026\n"
                "قيمة الهدر: 745,000 ريال\n"
                "النسبة: 31.8%\n"
                "الأثر المالي: 745,000 ريال"
            ),
            priority_rationale="العقود المتداخلة ثاني أكبر مصدر — تكرار التزامات دون قيمة.",
            impact="تضخيم التزامات تعاقدية.",
            root_cause="غير متوفر في البيانات.",
            decision="تجميد التجديدات التعاقدية المكررة حتى إتمام المراجعة.",
            priority="عالية",
            owner="غير محدد في البيانات",
            timeline="30–45 يوماً",
            savings="745,000 ريال.",
            kpi="دمج عقد مكرر خلال 60 يوماً.",
        )
        + "3.\n"
        + _executive_item(
            angle="الكفاءة التشغيلية",
            problem="عمليات التشغيل تساهم بهدر مادي.",
            evidence=(
                "الفئة: العمليات\n"
                "مجال الأعمال: التشغيل\n"
                "الإدارة: إدارة العمليات\n"
                "الفترة: الربع الثاني 2026\n"
                "قيمة الهدر: 520,000 ريال\n"
                "النسبة: 22.2%\n"
                "الأثر المالي: 520,000 ريال"
            ),
            priority_rationale="العمليات تمثل 22.2% — فرصة كفاءة تشغيلية.",
            impact="ارتفاع تكلفة الوحدة التشغيلية.",
            root_cause="غير متوفر في البيانات.",
            decision="تفعيل مراجعة كفاءة تشغيلية على بنود العمليات.",
            priority="متوسطة",
            owner="إدارة العمليات",
            timeline="60–90 يوماً",
            savings="520,000 ريال.",
            kpi="خفض بنود العمليات 8%.",
        )
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
        executive_summary: str = (
            "الوضع: خلال الربع الثاني 2026 بلغ إجمالي الهدر 2,340,000 ريال. "
            "المشكلة: الشؤون المالية 1,075,000 ريال (45.9%). "
            "القرار المطلوب: مراجعة حوكمة مالية فورية."
        ),
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
