"""Validate waste recommendations against Facts Contract evidence."""

from __future__ import annotations

from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.recommendation_parser import ParsedRecommendationItem
from app.business.facts.contract import FactsContract
from app.presentation.evidence_registry import EvidenceRegistry


def validate_waste_recommendations(
    items: tuple[ParsedRecommendationItem, ...],
    facts_contract: FactsContract,
) -> None:
    registry = EvidenceRegistry.from_contract(facts_contract)
    for item in items:
        combined = f"{item.title}\n{item.description}"
        if item.executive:
            combined = f"{combined}\n{item.executive.to_description()}"
        errors = registry.validate_text(combined)
        if item.executive and not item.executive.evidence:
            errors.append("missing_evidence_section")
        if errors:
            raise AiRecommendationError(
                "recommendation_evidence_failed",
                "Recommendation failed strict evidence validation",
                {
                    "item_index": item.index,
                    "errors": errors,
                },
            )
