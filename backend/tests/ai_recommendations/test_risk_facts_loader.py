"""Risk facts loader tests."""

from __future__ import annotations

import pytest

from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.facts_loader import load_risk_facts_contract
from tests.ai_recommendations.risk_conftest import sample_risk_runtime_metadata


def test_load_risk_facts_contract_success() -> None:
    metadata = sample_risk_runtime_metadata()
    contract = load_risk_facts_contract(metadata)
    assert contract.engine_id == "risk"


def test_load_risk_facts_rejects_waste_engine() -> None:
    from tests.ai_recommendations.conftest import sample_facts_contract

    metadata = {"facts_contract": sample_facts_contract().to_dict()}
    with pytest.raises(AiRecommendationError) as exc:
        load_risk_facts_contract(metadata)
    assert exc.value.error_code == "invalid_facts_contract"
