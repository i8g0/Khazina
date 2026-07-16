"""AI Simulation Explainer — results → executive narrative."""

from __future__ import annotations

import json
import re
from typing import Any

from app.ai.providers.factory import create_ai_provider
from app.business.engines.scenario.calculator import ScenarioCalculationResult
from app.scenario.ai_contract import InterpretedScenario, SimulationExplanation
from app.scenario.exceptions import ScenarioInterpretationError


_SYSTEM_PROMPT = """أنت مستشار مالي تنفيذي في منصة خزينة.
بعد تنفيذ محاكاة مالية، اكتب شرحاً تنفيذياً بالعربية بصيغة JSON فقط.

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
  "next_actions": ["...", "..."]
}

استخدم الأرقام من النتائج فقط. لا تخترع أرقاماً جديدة.
"""


class AISimulationExplainer:
    def explain(
        self,
        *,
        user_request: str,
        interpreted: InterpretedScenario,
        calculation: ScenarioCalculationResult,
    ) -> SimulationExplanation:
        context = self._results_context(user_request, interpreted, calculation)
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ]
        provider = create_ai_provider()
        try:
            raw = provider.chat(messages, format_json=True)
        finally:
            provider.close()

        payload = self._parse_json(raw)
        try:
            return SimulationExplanation.model_validate(payload)
        except Exception as exc:
            raise ScenarioInterpretationError(
                "invalid_explanation",
                f"AI explanation invalid: {exc}",
                {"raw": payload},
            ) from exc

    @staticmethod
    def _results_context(
        user_request: str,
        interpreted: InterpretedScenario,
        calculation: ScenarioCalculationResult,
    ) -> str:
        return (
            f"الطلب الأصلي:\n{user_request}\n\n"
            f"السيناريو المفسّر:\n{interpreted.summary_ar}\n"
            f"النوع: {interpreted.scenario_type}\n"
            f"الإجراءات: {json.dumps([a.model_dump() for a in interpreted.actions], ensure_ascii=False)}\n\n"
            f"النتائج:\n"
            f"- الأساس: {calculation.baseline_total:,.0f} SAR\n"
            f"- المتوقع: {calculation.projected_total:,.0f} SAR\n"
            f"- التغير: {calculation.delta_percent:.1f}%\n"
            f"- أفق: {calculation.horizon_quarters} أرباع\n"
            f"- الثقة: {calculation.confidence_percent}%\n"
        )

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
