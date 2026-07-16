"""Maps AI-native scenario results to simulation Gold persistence."""

from __future__ import annotations

from typing import Any

from app.business.engines.scenario.calculator import ScenarioCalculationResult
from app.db.models.enums import SimulationActionStatus
from app.scenario.ai_contract import FinancialRealityPayload, InterpretedScenario, SimulationExplanation
from app.scenario.mappers.scenario_gold import ScenarioGoldMapper


class AISimulationGoldMapper:
    @staticmethod
    def to_record_payload(
        calculation: ScenarioCalculationResult,
        *,
        interpreted: InterpretedScenario,
        explanation: SimulationExplanation,
        user_request: str,
        financial_reality: FinancialRealityPayload | None = None,
    ) -> dict[str, Any]:
        base = ScenarioGoldMapper.to_record_payload(calculation, facts=_FactsStub())
        sign = "+" if calculation.delta_percent > 0 else ""
        base["result_title"] = interpreted.title_ar
        base["result_description"] = (
            f"{interpreted.summary_ar} — فارق {sign}{calculation.delta_percent:.1f}% "
            f"على أفق {calculation.horizon_quarters} أرباع."
        )
        base["action_items"] = [
            {
                "title": item[:120],
                "description": explanation.executive_summary[:500],
                "status": SimulationActionStatus.PROPOSED.value,
            }
            for item in explanation.next_actions[:5]
        ] or [
            {
                "title": "توصية تنفيذية",
                "description": explanation.board_recommendation[:500],
                "status": SimulationActionStatus.PROPOSED.value,
            }
        ]
        base["ai_metadata"] = {
            "user_request": user_request,
            "interpreted_scenario": interpreted.to_dict(),
            "explanation": explanation.to_dict(),
            "executive_judgment": (
                explanation.executive_judgment.model_dump(mode="json")
                if explanation.executive_judgment
                else None
            ),
            "financial_reality": (
                financial_reality.model_dump(mode="json") if financial_reality else None
            ),
        }
        return base


class _FactsStub:
    contract_version = "1.0"
    engine_id = "scenario_ai_v1"
    engine_version = "1.0.0"
