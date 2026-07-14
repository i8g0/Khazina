"""Scenario Engine manifest — static engine identity."""

from __future__ import annotations

from app.business.manifest import EngineManifest

ENGINE_ID = "scenario"
ENGINE_NAME = "Business Scenario Engine"
ENGINE_VERSION = "1.0.0"
ENGINE_DESCRIPTION = (
    "Deterministic what-if scenario analysis — baseline vs projected outcomes"
)
FACTS_CONTRACT_VERSION = "1.0"

SUPPORTED_FACTS: tuple[str, ...] = (
    "scenario.archetype",
    "scenario.baseline_total",
    "scenario.projected_total",
    "scenario.delta_amount",
    "scenario.delta_percent",
    "scenario.horizon_quarters",
    "scenario.category_baseline",
    "scenario.category_projected",
    "scenario.confidence_percent",
)

SCENARIO_ENGINE_MANIFEST = EngineManifest(
    engine_id=ENGINE_ID,
    engine_name=ENGINE_NAME,
    engine_version=ENGINE_VERSION,
    engine_description=ENGINE_DESCRIPTION,
    supported_facts=SUPPORTED_FACTS,
    extensions={"facts_contract_version": FACTS_CONTRACT_VERSION},
)
