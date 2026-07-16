"""AI Simulation Explainer — results → executive narrative + financial judgment."""

from __future__ import annotations

import json
import re
from typing import Any

from app.ai.exceptions import AIConnectionError, AITimeoutError
from app.ai.providers.factory import create_ai_provider
from app.business.engines.scenario.calculator import ScenarioCalculationResult
from app.business.facts.contract import CONTRACT_VERSION, Fact, FactsContract
from app.presentation.evidence_registry import EvidenceRegistry
from app.presentation.narrative_guard import (
    NARRATIVE_LLM_UNAVAILABLE,
    apply_numbers_only_guard,
)
from app.scenario.ai_contract import (
    ExecutiveJudgmentPayload,
    FinancialRealityPayload,
    InterpretedScenario,
    SimulationExplanation,
)
from app.scenario.exceptions import ScenarioInterpretationError
from app.scenario.risk_context import SimulationRiskContext


_SYSTEM_PROMPT = """أنت مستشار مالي تنفيذي (مستوى Big Four) في منصة خزينة — وليس آلة حاسبة.
بعد محاكاة مقيّدة ببيانات المنشأة المرفوعة، اكتب تقريراً تنفيذياً بالعربية بصيغة JSON فقط.

قواعد الحكم التنفيذي (إلزامية):
1. حلّل الطلب مقابل حجم المنشأة — لا تبالغ في أثر استثمارات صغيرة.
2. احسب واذكر هل التغيير جوهري (material) أم هامشياً — استخدم «الحكم المالي المحسوب مسبقاً» حرفياً للنسب.
3. قيّم واقعية التنفيذ — إن كانت الميزانية غير كافية للفرع/المشروع، قل ذلك بوضوح.
4. قارن دائماً بالإنفاق الحالي والإيرادات التقديرية وميزانية الإدارة — لا تحلّل رقماً معزولاً.
5. قدّم بديلاً استراتيجياً — لا تكتفِ بـ «لا أثر».
6. اختم بتوصية واحدة فقط: الموافقة | الموافقة مع تعديلات | التأجيل | الرفض — مع المبرر.
7. لا تخترع ثقة — إن البيانات ناقصة، قل: «البيانات المتاحة غير كافية لتقدير بثقة عالية».
8. لا تخترع أرقاماً غير موجودة في السياق أو في الحكم المحسوب.

أعد JSON:
{
  "executive_summary": "...",
  "expected_impact": "...",
  "financial_changes": "...",
  "risks": "...",
  "benefits": "...",
  "confidence": "...",
  "assumptions": "...",
  "board_recommendation": "...",
  "next_actions": ["...", "..."],
  "forecast_ranges": "..."
}

لا تضف حقل executive_judgment — يُرفق آلياً من المحرك المالي.
"""


class AISimulationExplainer:
    def explain(
        self,
        *,
        user_request: str,
        interpreted: InterpretedScenario,
        calculation: ScenarioCalculationResult,
        financial_reality: FinancialRealityPayload | None = None,
        risk_context: SimulationRiskContext | None = None,
        executive_judgment: ExecutiveJudgmentPayload | None = None,
    ) -> SimulationExplanation:
        context = self._results_context(
            user_request,
            interpreted,
            calculation,
            financial_reality,
            risk_context,
            executive_judgment,
        )
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ]
        provider = create_ai_provider()
        registry = _build_scenario_registry(calculation, financial_reality)
        try:
            try:
                raw = provider.chat(messages, format_json=True)
            except (AIConnectionError, AITimeoutError):
                if executive_judgment is None:
                    raise
                return _judgment_fallback_explanation(
                    executive_judgment, narrative_status=NARRATIVE_LLM_UNAVAILABLE
                )

            payload = self._parse_json(raw)
            if executive_judgment is not None:
                payload = merge_payload_judgment(payload, executive_judgment)

            def retry_narrative(addendum: str) -> str:
                extended = [*messages, {"role": "system", "content": addendum}]
                retry_raw = provider.chat(extended, format_json=True)
                retry_payload = self._parse_json(retry_raw)
                if executive_judgment is not None:
                    retry_payload = merge_payload_judgment(
                        retry_payload, executive_judgment
                    )
                return _combine_explanation_narrative(retry_payload)

            _, guard_status = apply_numbers_only_guard(
                registry,
                _combine_explanation_narrative(payload),
                retry=retry_narrative,
            )
            if guard_status and executive_judgment is not None:
                return _judgment_fallback_explanation(
                    executive_judgment, narrative_status=guard_status
                )
            if guard_status:
                raise ScenarioInterpretationError(
                    "narrative_guard_rejected",
                    "Scenario AI narrative rejected by number guard",
                )

            try:
                return SimulationExplanation.model_validate(payload)
            except Exception as exc:
                if executive_judgment is not None:
                    return SimulationExplanation(
                        executive_summary=payload.get(
                            "executive_summary",
                            executive_judgment.executive_verdict,
                        ),
                        expected_impact=str(
                            payload.get(
                                "expected_impact",
                                executive_judgment.materiality_analysis,
                            )
                        ),
                        financial_changes=str(
                            payload.get(
                                "financial_changes",
                                executive_judgment.scale_comparison,
                            )
                        ),
                        risks=str(
                            payload.get("risks", executive_judgment.remaining_risks)
                        ),
                        benefits=str(
                            payload.get("benefits", executive_judgment.strategic_advice)
                        ),
                        confidence=str(
                            payload.get(
                                "confidence",
                                executive_judgment.confidence_statement,
                            )
                        ),
                        assumptions=str(
                            payload.get(
                                "assumptions",
                                "؛ ".join(executive_judgment.assumptions_used),
                            )
                        ),
                        board_recommendation=str(
                            payload.get(
                                "board_recommendation",
                                executive_judgment.strategic_recommendation,
                            )
                        ),
                        next_actions=payload.get("next_actions")
                        or [executive_judgment.next_step],
                        forecast_ranges=str(payload.get("forecast_ranges", "")),
                        executive_judgment=executive_judgment,
                    )
                raise ScenarioInterpretationError(
                    "invalid_explanation",
                    f"AI explanation invalid: {exc}",
                    {"raw": payload},
                ) from exc
        finally:
            provider.close()

    @staticmethod
    def _results_context(
        user_request: str,
        interpreted: InterpretedScenario,
        calculation: ScenarioCalculationResult,
        financial_reality: FinancialRealityPayload | None,
        risk_context: SimulationRiskContext | None = None,
        executive_judgment: ExecutiveJudgmentPayload | None = None,
    ) -> str:
        lines = [
            f"الطلب الأصلي:\n{user_request}\n",
            f"السيناريو المفسّر:\n{interpreted.summary_ar}",
            f"النوع: {interpreted.scenario_type}",
            f"الإجراءات: {json.dumps([a.model_dump() for a in interpreted.actions], ensure_ascii=False)}\n",
            "نتائج الإنفاق:",
            f"- الأساس: {calculation.baseline_total:,.0f} SAR",
            f"- المتوقع: {calculation.projected_total:,.0f} SAR",
            f"- التغير: {calculation.delta_percent:.1f}%",
            f"- أفق: {calculation.horizon_quarters} أرباع",
            f"- الثقة المحسوبة: {calculation.confidence_percent}%",
        ]
        if executive_judgment is not None:
            lines.append("\n=== الحكم المالي المحسوب مسبقاً (استخدمه حرفياً — لا تغيّر النسب) ===")
            lines.append(json.dumps(executive_judgment.model_dump(mode="json"), ensure_ascii=False, indent=2))
            lines.append(
                "\nالمطلوب: ادمج هذا الحكم في executive_summary و board_recommendation و confidence. "
                f"التوصية المعتمدة: {executive_judgment.recommendation}."
            )
        if financial_reality:
            lines.append("\nقيود الواقع المالي (استخدمها حرفياً):")
            lines.append(
                f"- ثقة: {financial_reality.confidence_level} "
                f"({financial_reality.confidence_score}/100) — {financial_reality.confidence_rationale}"
            )
            ec = financial_reality.expense_change
            lines.append(
                f"- تغير الإنفاق: أسوأ {ec.worst:,.0f} | متوقع {ec.expected:,.0f} | أفضل {ec.best:,.0f} SAR"
            )
            if financial_reality.revenue_impact:
                rev = financial_reality.revenue_impact
                lines.append(
                    f"- تأثير الإيرادات: أسوأ {rev.worst:,.0f} | متوقع {rev.expected:,.0f} | "
                    f"أفضل {rev.best:,.0f} SAR"
                )
            cash = financial_reality.cash_impact
            lines.append(
                f"- الأثر على السيولة: أسوأ {cash.worst:,.0f} | متوقع {cash.expected:,.0f} | "
                f"أفضل {cash.best:,.0f} SAR"
            )
            if financial_reality.action_reasonings:
                lines.append("التبريرات المحسوبة:")
                lines.extend(f"  • {r}" for r in financial_reality.action_reasonings)
            if financial_reality.validation_notes:
                lines.append("تعديلات التحقق المالي:")
                lines.extend(f"  • {n}" for n in financial_reality.validation_notes)
            if financial_reality.assumptions_used:
                lines.append("الافتراضات:")
                lines.extend(f"  • {a}" for a in financial_reality.assumptions_used)
        if risk_context is not None:
            lines.append("\n" + risk_context.to_prompt_block())
            lines.append(
                "\nالمطلوب في حقل risks: اشرح كيف ستؤثر هذه المخاطر على السيناريو المقترح "
                "بالأرقام والإدارات والموردين من السياق أعلاه."
            )
        return "\n".join(lines)

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ScenarioInterpretationError("invalid_explanation_json", "Expected JSON object")
        return data


def merge_payload_judgment(
    payload: dict[str, Any],
    judgment: ExecutiveJudgmentPayload,
) -> dict[str, Any]:
    merged = dict(payload)
    merged["executive_judgment"] = judgment.model_dump(mode="json")
    if not merged.get("board_recommendation"):
        merged["board_recommendation"] = judgment.strategic_recommendation
    if not merged.get("confidence"):
        merged["confidence"] = judgment.confidence_statement
    if not merged.get("executive_summary"):
        merged["executive_summary"] = judgment.executive_verdict
    return merged


def _combine_explanation_narrative(payload: dict[str, Any]) -> str:
    parts = [
        str(payload.get("executive_summary", "")),
        str(payload.get("expected_impact", "")),
        str(payload.get("financial_changes", "")),
        str(payload.get("risks", "")),
        str(payload.get("benefits", "")),
        str(payload.get("board_recommendation", "")),
        str(payload.get("forecast_ranges", "")),
    ]
    return "\n".join(p for p in parts if p.strip())


def _build_scenario_registry(
    calculation: ScenarioCalculationResult,
    financial_reality: FinancialRealityPayload | None,
) -> EvidenceRegistry:
    facts: list[Fact] = [
        Fact(
            domain="simulation",
            metric="baseline_total",
            value=f"{calculation.baseline_total:.2f}",
            source="scenario_engine",
            unit="currency",
        ),
        Fact(
            domain="simulation",
            metric="projected_total",
            value=f"{calculation.projected_total:.2f}",
            source="scenario_engine",
            unit="currency",
        ),
        Fact(
            domain="simulation",
            metric="delta_percent",
            value=f"{calculation.delta_percent:.2f}",
            source="scenario_engine",
            unit="percent",
        ),
        Fact(
            domain="simulation",
            metric="confidence_percent",
            value=f"{calculation.confidence_percent:.2f}",
            source="scenario_engine",
            unit="percent",
        ),
    ]
    if financial_reality is not None:
        ec = financial_reality.expense_change
        for label, amount in (
            ("expense_worst", ec.worst),
            ("expense_expected", ec.expected),
            ("expense_best", ec.best),
        ):
            facts.append(
                Fact(
                    domain="simulation",
                    metric=label,
                    value=f"{amount:.2f}",
                    source="financial_reality",
                    unit="currency",
                )
            )
        facts.append(
            Fact(
                domain="simulation",
                metric="confidence_score",
                value=str(financial_reality.confidence_score),
                source="financial_reality",
                unit="percent",
            )
        )
    contract = FactsContract(
        contract_version=CONTRACT_VERSION,
        engine_id="scenario_ai_v1",
        engine_version="1.0.0",
        generated_at=calculation.generated_at,
        facts=tuple(facts),
    )
    return EvidenceRegistry.from_contract(contract)


def _judgment_fallback_explanation(
    judgment: ExecutiveJudgmentPayload,
    *,
    narrative_status: str,
) -> SimulationExplanation:
    return SimulationExplanation(
        executive_summary=judgment.executive_verdict,
        expected_impact=judgment.materiality_analysis,
        financial_changes=judgment.scale_comparison,
        risks=judgment.remaining_risks,
        benefits=judgment.strategic_advice,
        confidence=judgment.confidence_statement,
        assumptions="؛ ".join(judgment.assumptions_used),
        board_recommendation=judgment.strategic_recommendation,
        next_actions=[judgment.next_step],
        forecast_ranges="",
        executive_judgment=judgment,
        narrative_status=narrative_status,
    )
