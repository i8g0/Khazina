"""Risk mitigation parser tests."""

from __future__ import annotations

from app.ai_recommendations.risk_recommendation_parser import parse_risk_mitigation_text
from tests.ai_recommendations.risk_conftest import sample_risk_mitigation_text


def test_parse_risk_mitigation_text_extracts_categories() -> None:
    items = parse_risk_mitigation_text(sample_risk_mitigation_text())
    assert len(items) == 5
    assert items[0].category_code == "immediate_action"
    assert items[1].category_code == "monitoring_action"
    assert items[0].title
