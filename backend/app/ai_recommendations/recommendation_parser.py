"""Parse RECOMMENDATIONS task output into structured items (§11 contract)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.ai_recommendations.constants import (
    MAX_RECOMMENDATION_ITEMS,
    MAX_TITLE_LENGTH,
    MIN_RECOMMENDATION_ITEMS,
    PRIORITY_HIGH_KEYWORDS,
    PRIORITY_MEDIUM_KEYWORDS,
)
from app.ai_recommendations.exceptions import AiRecommendationError

_NUMBERED_SPLIT = re.compile(
    r"(?=(?:^\s*(?:\d+|[\u0660-\u0669]+)\.\s+))",
    re.MULTILINE,
)


@dataclass(frozen=True, slots=True)
class ParsedRecommendationItem:
    index: int
    title: str
    description: str
    priority: str


def parse_recommendations_text(text: str) -> tuple[ParsedRecommendationItem, ...]:
    cleaned = text.strip()
    if not cleaned:
        raise AiRecommendationError(
            "invalid_recommendation_count",
            "Recommendations text is empty",
        )

    chunks = [
        chunk.strip()
        for chunk in _NUMBERED_SPLIT.split(cleaned)
        if chunk.strip()
    ]
    if not chunks:
        chunks = [cleaned]

    items: list[ParsedRecommendationItem] = []
    for index, chunk in enumerate(chunks):
        body = re.sub(r"^\s*(?:\d+|[\u0660-\u0669]+)\.\s+", "", chunk).strip()
        if not body:
            raise AiRecommendationError(
                "missing_recommendation_title",
                "Recommendation item is empty",
                {"item_index": index},
            )
        title, description = _split_title_and_description(body)
        if not title:
            raise AiRecommendationError(
                "missing_recommendation_title",
                "Recommendation item missing action/title",
                {"item_index": index},
            )
        items.append(
            ParsedRecommendationItem(
                index=index,
                title=title,
                description=description or title,
                priority=_map_priority(body),
            )
        )

    if not MIN_RECOMMENDATION_ITEMS <= len(items) <= MAX_RECOMMENDATION_ITEMS:
        raise AiRecommendationError(
            "invalid_recommendation_count",
            "Recommendation count must be between 3 and 6",
            {"count": len(items)},
        )
    return tuple(items)


def _split_title_and_description(body: str) -> tuple[str, str]:
    for separator in (". ", "。\n", "\n"):
        if separator in body:
            head, tail = body.split(separator, 1)
            title = head.strip()
            description = body.strip()
            if len(title) > MAX_TITLE_LENGTH:
                title = title[: MAX_TITLE_LENGTH - 3].rstrip() + "..."
            return title, description
    title = body.strip()
    if len(title) > MAX_TITLE_LENGTH:
        return title[: MAX_TITLE_LENGTH - 3].rstrip() + "...", body.strip()
    return title, body.strip()


def _map_priority(text: str) -> str:
    lowered = text.lower()
    tokens = set(re.findall(r"[\w\u0600-\u06FF]+", lowered))
    if tokens & PRIORITY_HIGH_KEYWORDS:
        return "high"
    if tokens & PRIORITY_MEDIUM_KEYWORDS:
        return "medium"
    return "medium"
