"""Rehydrate Facts Contract from completed analysis runs."""

from __future__ import annotations

from typing import Any

from app.ai_recommendations.exceptions import AiRecommendationError
from app.business.facts.contract import CONTRACT_VERSION, FactsContract


def load_facts_contract(
    runtime_metadata: dict[str, Any] | None,
    *,
    expected_engine_id: str = "waste",
) -> FactsContract:
    if not runtime_metadata:
        raise AiRecommendationError(
            "missing_facts_contract",
            "Analysis run has no runtime metadata",
        )
    payload = runtime_metadata.get("facts_contract")
    if not isinstance(payload, dict):
        raise AiRecommendationError(
            "missing_facts_contract",
            "Analysis run runtime_metadata.facts_contract is missing or invalid",
        )
    try:
        contract = FactsContract.from_dict(payload)
    except (KeyError, TypeError, ValueError) as exc:
        raise AiRecommendationError(
            "invalid_facts_contract",
            "Facts Contract payload cannot be rehydrated",
        ) from exc
    if contract.contract_version != CONTRACT_VERSION:
        raise AiRecommendationError(
            "invalid_facts_contract",
            f"Unsupported contract_version '{contract.contract_version}'",
            {"expected": CONTRACT_VERSION},
        )
    if contract.engine_id != expected_engine_id:
        raise AiRecommendationError(
            "invalid_facts_contract",
            f"Unsupported engine_id '{contract.engine_id}' "
            f"(expected '{expected_engine_id}')",
        )
    return contract


def load_risk_facts_contract(runtime_metadata: dict[str, Any] | None) -> FactsContract:
    return load_facts_contract(runtime_metadata, expected_engine_id="risk")
