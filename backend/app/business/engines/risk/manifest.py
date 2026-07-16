"""Risk Engine manifest — static engine identity."""

from __future__ import annotations

from app.business.manifest import EngineManifest

ENGINE_ID = "risk"
ENGINE_NAME = "Financial Risk Engine"
ENGINE_VERSION = "1.0.0"
ENGINE_DESCRIPTION = (
    "Deterministic financial risk intelligence — detection, classification, and scoring"
)
FACTS_CONTRACT_VERSION = "1.0"

SUPPORTED_FACTS: tuple[str, ...] = (
    "risk.total_findings",
    "risk.high_priority_count",
    "risk.medium_priority_count",
    "risk.low_priority_count",
    "risk.overall_posture_level",
    "risk.top_category",
    "risk.liquidity_ratio",
    "risk.score_max",
    "risk.waste_percentage",
    "risk.category_count",
)

RISK_ENGINE_MANIFEST = EngineManifest(
    engine_id=ENGINE_ID,
    engine_name=ENGINE_NAME,
    engine_version=ENGINE_VERSION,
    engine_description=ENGINE_DESCRIPTION,
    supported_facts=SUPPORTED_FACTS,
    extensions={"facts_contract_version": FACTS_CONTRACT_VERSION},
)
