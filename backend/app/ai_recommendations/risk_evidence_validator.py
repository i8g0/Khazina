"""Validate risk recommendations against Facts Contract evidence."""

from __future__ import annotations

from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.risk_recommendation_parser import ParsedRiskRecommendationItem
from app.business.facts.contract import FactsContract
from app.presentation.evidence_registry import EvidenceRegistry


def validate_risk_recommendations(
    items: tuple[ParsedRiskRecommendationItem, ...],
    facts_contract: FactsContract,
) -> None:
    registry = EvidenceRegistry.from_contract(facts_contract)
    for item in items:
        combined = f"{item.title}\n{item.description}"
        errors = registry.validate_risk_text(combined)
        if errors:
            raise AiRecommendationError(
                "recommendation_evidence_failed",
                "Risk recommendation failed strict evidence validation",
                {
                    "item_index": item.index,
                    "errors": errors,
                },
            )
