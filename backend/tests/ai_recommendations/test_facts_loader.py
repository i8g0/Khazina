"""Facts rehydration tests."""

from __future__ import annotations

import pytest

from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.facts_loader import load_facts_contract
from tests.ai_recommendations.conftest import sample_facts_contract


def test_load_valid_facts_contract() -> None:
    contract = sample_facts_contract()
    loaded = load_facts_contract({"facts_contract": contract.to_dict()})
    assert loaded.engine_id == "waste"
    assert loaded.contract_version == "1.0"


def test_rejects_missing_facts_contract() -> None:
    with pytest.raises(AiRecommendationError) as exc:
        load_facts_contract({})
    assert exc.value.error_code == "missing_facts_contract"
