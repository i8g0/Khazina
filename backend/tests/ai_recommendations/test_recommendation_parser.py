"""Recommendation parser unit tests."""

from __future__ import annotations

import pytest

from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.recommendation_parser import parse_recommendations_text


def _three_item_lines(prefix_template: str) -> str:
    return "\n".join(
        prefix_template.format(n=n) + f" توصية {n}" for n in (1, 2, 3)
    )


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


@pytest.mark.parametrize(
    ("name", "text"),
    [
        ("plain_arabic_numerals", _three_item_lines("{n}. ").replace("1", "١").replace("2", "٢").replace("3", "٣")),
        ("markdown_h2", _three_item_lines("## {n}. ")),
        ("markdown_h3", _three_item_lines("### {n}. ")),
        ("markdown_h4", _three_item_lines("#### {n}. ")),
        ("markdown_bold_open", _three_item_lines("**{n}. ")),
        ("markdown_bold_closed", _three_item_lines("**{n}.** ")),
        ("markdown_underscore_closed", _three_item_lines("__{n}.__ ")),
    ],
)
def test_parse_three_recommendations_markdown_formats(name: str, text: str) -> None:
    del name
    items = parse_recommendations_text(text)
    assert len(items) == 3
    assert all(item.title for item in items)


def test_parse_bold_numbered_items_from_llm_shape() -> None:
    text = (
        "مقدمة قصيرة.\n\n"
        "**1. أول إجراء**\n"
        "تفاصيل الأول.\n"
        "**2. ثاني إجراء**\n"
        "تفاصيل الثاني.\n"
        "**3. ثالث إجراء**\n"
        "تفاصيل الثالث."
    )
    items = parse_recommendations_text(text)
    assert len(items) == 4
    assert "مقدمة قصيرة" in items[0].title


def test_rejects_too_few_items() -> None:
    with pytest.raises(AiRecommendationError) as exc:
        parse_recommendations_text("1. واحد فقط\n2. اثنان فقط")
    assert exc.value.error_code == "invalid_recommendation_count"


def test_rejects_too_many_items() -> None:
    text = "\n".join(f"{i}. عنصر {i}" for i in range(1, 8))
    with pytest.raises(AiRecommendationError) as exc:
        parse_recommendations_text(text)
    assert exc.value.error_code == "invalid_recommendation_count"
