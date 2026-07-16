"""AI Scenario Interpreter — natural language → structured scenario JSON."""

from __future__ import annotations

import json
import re
from typing import Any

from app.ai.providers.factory import create_ai_provider
from app.business.engines.scenario.input import ScenarioBaselineInput
from app.scenario.ai_contract import InterpretedScenario, ScenarioAction
from app.scenario.exceptions import ScenarioInterpretationError


_SYSTEM_PROMPT = """أنت محلل مالي تنفيذي في منصة خزينة.
مهمتك: تحويل طلب المدير باللغة الطبيعية إلى سيناريo مالي منظم بصيغة JSON فقط.

قواعد:
- افهم النية التجارية وليس الكلمات فقط.
- استخرج النسب والمبالغ والعملة (SAR افتراضياً).
- أنشئ actions متعددة عند الحاجة (mixed scenarios).
- action_type يجب أن يكون أحد:
  reduce_expense, increase_revenue, reduce_budget, increase_budget, reduce_waste,
  increase_profit, reduce_suppliers, close_branches, hire_employees, increase_payroll,
  increase_prices, reduce_transport, investment, operational_change, mixed
- mode: percent | absolute | count
- category/department عند التخصيص (finance, marketing, operations, procurement, it, hr, logistics, legal, travel, ...)
- horizon_quarters: 1-12 (افتراضي 4)
- confidence: 0-100

أعد JSON فقط بهذا الشكل:
{
  "scenario_type": "...",
  "title_ar": "...",
  "summary_ar": "...",
  "target_amount": null,
  "currency": "SAR",
  "horizon_quarters": 4,
  "actions": [{"action_type":"...", "mode":"percent|absolute|count", "value": null, "amount": null, "category": null, "department": null, "description": "..."}],
  "assumptions": ["..."],
  "confidence": 75
}
"""


class AIScenarioInterpreter:
    """Calls CloudProvider to interpret executive natural-language requests."""

    def interpret(
        self,
        user_request: str,
        *,
        baseline: ScenarioBaselineInput,
    ) -> InterpretedScenario:
        cleaned = user_request.strip()
        if not cleaned:
            raise ScenarioInterpretationError("empty_request", "Scenario request must not be empty")

        baseline_context = self._baseline_context(baseline)
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"طلب المدير:\n{cleaned}\n\n"
                    f"خط الأساس المالي:\n{baseline_context}\n\n"
                    "حوّل الطلب إلى JSON منظم."
                ),
            },
        ]

        provider = create_ai_provider()
        try:
            raw = provider.chat(messages, format_json=True)
        finally:
            provider.close()

        payload = self._parse_json(raw)
        try:
            return InterpretedScenario.model_validate(payload)
        except Exception as exc:
            raise ScenarioInterpretationError(
                "invalid_interpretation",
                f"AI returned invalid scenario structure: {exc}",
                {"raw": payload},
            ) from exc

    @staticmethod
    def _baseline_context(baseline: ScenarioBaselineInput) -> str:
        lines = [f"إجمالي الإنفاق: {baseline.total_baseline:,.0f} SAR"]
        for cat in baseline.categories[:20]:
            lines.append(f"- {cat.category_name}: {cat.amount:,.0f} SAR")
        return "\n".join(lines)

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ScenarioInterpretationError(
                "invalid_ai_json",
                "AI response was not valid JSON",
                {"raw_preview": raw[:500]},
            ) from exc
        if not isinstance(data, dict):
            raise ScenarioInterpretationError(
                "invalid_ai_json",
                "AI response must be a JSON object",
            )
        return data
