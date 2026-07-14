"""Recommendation parser unit tests."""

from __future__ import annotations

import pytest

from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.recommendation_parser import parse_recommendations_text


def test_parse_three_recommendations() -> None:
    text = (
        "1. إجراء أول — أولوية عالية\n"
        "2. إجراء ثان — أولوية متوسطة\n"
        "3. إجراء ثالث"
    )
    items = parse_recommendations_text(text)
    assert len(items) == 3
    assert items[0].priority == "high"
    assert items[1].priority == "medium"
    assert items[0].title


def test_rejects_too_few_items() -> None:
    with pytest.raises(AiRecommendationError) as exc:
        parse_recommendations_text("1. واحد فقط\n2. اثنان فقط")
    assert exc.value.error_code == "invalid_recommendation_count"


def test_rejects_too_many_items() -> None:
    text = "\n".join(f"{i}. عنصر {i}" for i in range(1, 8))
    with pytest.raises(AiRecommendationError) as exc:
        parse_recommendations_text(text)
    assert exc.value.error_code == "invalid_recommendation_count"
