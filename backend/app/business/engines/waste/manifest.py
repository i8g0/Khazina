"""Waste Engine manifest — static engine identity."""

from __future__ import annotations

from app.business.manifest import EngineManifest

ENGINE_ID = "waste"
ENGINE_NAME = "Financial Waste Engine"
ENGINE_VERSION = "1.0.0"
ENGINE_DESCRIPTION = (
    "Deterministic financial waste analysis — cost leakage and inefficiency metrics"
)
FACTS_CONTRACT_VERSION = "1.1"

SUPPORTED_FACTS: tuple[str, ...] = (
    "waste.total_amount",
    "waste.percentage",
    "waste.top_category",
    "waste.top_category_percentage",
    "waste.potential_savings",
    "waste.savings_opportunities",
    "waste.category_amount",
    "waste.category_percentage",
    "waste.overall_level",
    "waste.category_level",
    "waste.reporting_period",
    "waste.category_count",
    "waste.currency",
    "waste.evidence_source",
    "waste.financial_impact",
    "waste.savings_opportunity",
)

WASTE_ENGINE_MANIFEST = EngineManifest(
    engine_id=ENGINE_ID,
    engine_name=ENGINE_NAME,
    engine_version=ENGINE_VERSION,
    engine_description=ENGINE_DESCRIPTION,
    supported_facts=SUPPORTED_FACTS,
    extensions={"facts_contract_version": FACTS_CONTRACT_VERSION},
)
