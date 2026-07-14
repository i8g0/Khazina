"""Maps Scenario Engine output to simulation Gold persistence payloads."""

from __future__ import annotations

from typing import Any

from app.business.engines.scenario.calculator import ScenarioCalculationResult
from app.business.engines.scenario.input import ScenarioArchetype
from app.business.facts.contract import FactsContract
from app.db.models.enums import SimulationActionStatus


class ScenarioGoldMapper:
    """Deterministic ScenarioCalculationResult → SimulationService result payload."""

    @staticmethod
    def to_record_payload(
        calculation: ScenarioCalculationResult,
        facts: FactsContract,
    ) -> dict[str, Any]:
        _ = facts
        delta_sign = "+" if calculation.delta_percent > 0 else ""
        return {
            "result_title": ScenarioGoldMapper._result_title(calculation),
            "result_description": ScenarioGoldMapper._result_description(calculation),
            "confidence_label": f"{calculation.confidence_percent}%",
            "forecast_summary": {
                "baseline_label": "الأساس",
                "baseline_value": ScenarioGoldMapper._display_currency(
                    calculation.baseline_total
                ),
                "projected_label": "المتوقع",
                "projected_value": ScenarioGoldMapper._display_currency(
                    calculation.projected_total
                ),
                "delta_label": "التغير",
                "delta_value": f"{delta_sign}{calculation.delta_percent:.1f}%",
                "confidence_label": f"{calculation.confidence_percent}%",
            },
            "chart_points": [
                {
                    "quarter_label": point.quarter_label,
                    "quarter_order": point.quarter_order,
                    "baseline_amount": point.baseline_amount,
                    "projected_amount": point.projected_amount,
                }
                for point in calculation.chart_points
            ],
            "comparison_metrics": [
                {
                    "metric_name": metric.metric_name,
                    "current_value": metric.current_value,
                    "simulated_value": metric.simulated_value,
                    "change_value": metric.change_value,
                    "direction": metric.direction,
                    "display_order": order,
                }
                for order, metric in enumerate(calculation.comparison_metrics)
            ],
            "impact_items": [
                {
                    "category_label": item.category_name,
                    "baseline_value": ScenarioGoldMapper._display_compact(
                        item.baseline_amount
                    ),
                    "projected_value": ScenarioGoldMapper._display_compact(
                        item.projected_amount
                    ),
                    "change_value": ScenarioGoldMapper._format_change_percent(
                        item.baseline_amount, item.change_amount
                    ),
                    "direction": item.direction,
                    "display_order": order,
                }
                for order, item in enumerate(calculation.categories)
            ],
            "action_items": ScenarioGoldMapper._action_items(calculation),
        }

    @staticmethod
    def _result_title(calculation: ScenarioCalculationResult) -> str:
        if calculation.archetype == ScenarioArchetype.SPENDING_REDUCTION:
            return "نتائج سيناريو تقليل الإنفاق"
        if calculation.archetype == ScenarioArchetype.SUPPLIER_CONSOLIDATION:
            return "نتائج سيناريو دمج الموردين"
        return "نتائج سيناريو توسع السوق"

    @staticmethod
    def _result_description(calculation: ScenarioCalculationResult) -> str:
        sign = "+" if calculation.delta_percent > 0 else ""
        return (
            f"مقارنة الأساس ({ScenarioGoldMapper._display_currency(calculation.baseline_total)}) "
            f"بالمتوقع ({ScenarioGoldMapper._display_currency(calculation.projected_total)}) "
            f"بفارق {sign}{calculation.delta_percent:.1f}% على أفق "
            f"{calculation.horizon_quarters} أرباع."
        )

    @staticmethod
    def _action_items(calculation: ScenarioCalculationResult) -> list[dict[str, str]]:
        if calculation.archetype == ScenarioArchetype.SPENDING_REDUCTION:
            return [
                {
                    "title": "مراجعة بنود الإنفاق عالية التأثير",
                    "description": "تحديد الفئات ذات أكبر مساهمة في الإنفاق وإعداد خطة خفض متدرجة.",
                    "status": SimulationActionStatus.PROPOSED.value,
                }
            ]
        if calculation.archetype == ScenarioArchetype.SUPPLIER_CONSOLIDATION:
            return [
                {
                    "title": "إطلاق خطة دمج الموردين",
                    "description": "تجميع العقود ضمن الموردين المستهدفين وتقليل التكاليف الإدارية.",
                    "status": SimulationActionStatus.PROPOSED.value,
                }
            ]
        return [
            {
                "title": "تقييم جدوى التوسع",
                "description": "مراجعة تكلفة التوسع مقابل نمو الإيرادات المتوقع قبل الالتزام التشغيلي.",
                "status": SimulationActionStatus.PROPOSED.value,
            }
        ]

    @staticmethod
    def _display_currency(value: float) -> str:
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M ر.س"
        if abs(value) >= 1_000:
            return f"{value / 1_000:.1f}K ر.س"
        return f"{value:.0f} ر.س"

    @staticmethod
    def _display_compact(value: float) -> str:
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        if abs(value) >= 1_000:
            return f"{value / 1_000:.1f}K"
        return f"{value:.0f}"

    @staticmethod
    def _format_change_percent(baseline: float, change: float) -> str:
        if baseline == 0:
            return "0%"
        pct = (change / baseline) * 100
        sign = "+" if pct > 0 else ""
        return f"{sign}{pct:.1f}%"
