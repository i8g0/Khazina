"""Maps Waste Engine Facts Contract to Gold persistence structures."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.business.facts.contract import FactsContract


class WasteGoldMapper:
    """Deterministic Facts Contract → ``WasteService.record_result`` payload."""

    @staticmethod
    def to_record_payload(facts: FactsContract) -> dict[str, Any]:
        by_metric = {fact.metric: fact for fact in facts.facts}

        total_waste = WasteGoldMapper._require_metric(by_metric, "waste.total_amount")
        waste_pct = WasteGoldMapper._require_metric(by_metric, "waste.percentage")
        potential_savings = by_metric.get("waste.potential_savings")
        opportunities = by_metric.get("waste.savings_opportunities")
        top_category = by_metric.get("waste.top_category")
        top_category_pct = by_metric.get("waste.top_category_percentage")

        breakdowns: list[dict[str, Any]] = []
        amount_facts = [
            fact
            for fact in facts.facts
            if fact.metric == "waste.category_amount"
        ]
        pct_by_category = {
            fact.metadata.get("category_name"): fact.value
            for fact in facts.facts
            if fact.metric == "waste.category_percentage"
        }
        for order, fact in enumerate(
            sorted(amount_facts, key=lambda item: item.metadata.get("category_name", ""))
        ):
            category_name = str(fact.metadata.get("category_name", ""))
            breakdowns.append(
                {
                    "category_name": category_name,
                    "amount": float(Decimal(fact.value)),
                    "percentage": float(Decimal(pct_by_category[category_name])),
                    "display_order": order,
                }
            )

        return {
            "total_waste_amount": float(Decimal(total_waste.value)),
            "waste_percentage": float(Decimal(waste_pct.value)),
            "top_category_name": top_category.value if top_category else None,
            "top_category_percentage": (
                float(Decimal(top_category_pct.value))
                if top_category_pct is not None
                else None
            ),
            "potential_savings_amount": (
                float(Decimal(potential_savings.value))
                if potential_savings is not None
                else None
            ),
            "active_savings_opportunities": (
                int(opportunities.value) if opportunities is not None else None
            ),
            "category_breakdowns": breakdowns,
        }

    @staticmethod
    def _require_metric(by_metric: dict[str, Any], metric: str) -> Any:
        if metric not in by_metric:
            raise KeyError(f"Missing required fact metric: {metric}")
        return by_metric[metric]
