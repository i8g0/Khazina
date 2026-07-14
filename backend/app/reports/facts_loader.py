"""Rehydrate Facts Contract for report generation (read-only)."""

from __future__ import annotations

from typing import Any

from app.business.facts.contract import CONTRACT_VERSION, FactsContract
from app.reports.constants import SUPPORTED_ENGINE_IDS
from app.reports.exceptions import ReportBuilderError


def load_facts_contract(runtime_metadata: dict[str, Any] | None) -> FactsContract:
    if not runtime_metadata:
        raise ReportBuilderError(
            "missing_facts_contract",
            "Analysis run has no runtime metadata",
        )
    payload = runtime_metadata.get("facts_contract")
    if not isinstance(payload, dict):
        raise ReportBuilderError(
            "missing_facts_contract",
            "Analysis run runtime_metadata.facts_contract is missing or invalid",
        )
    try:
        contract = FactsContract.from_dict(payload)
    except (KeyError, TypeError, ValueError) as exc:
        raise ReportBuilderError(
            "invalid_facts_contract",
            "Facts Contract payload cannot be rehydrated",
        ) from exc
    if contract.contract_version != CONTRACT_VERSION:
        raise ReportBuilderError(
            "invalid_facts_contract",
            f"Unsupported contract_version '{contract.contract_version}'",
            {"expected": CONTRACT_VERSION},
        )
    if contract.engine_id not in SUPPORTED_ENGINE_IDS:
        raise ReportBuilderError(
            "invalid_facts_contract",
            f"Unsupported engine_id '{contract.engine_id}' for report generation",
        )
    return contract
