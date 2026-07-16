"""Parse RISK_MITIGATION_OPTIONS task output into categorized items."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.ai_recommendations.constants import MAX_TITLE_LENGTH
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.recommendation_parser import (
    _map_priority,
    _NUMBERED_PREFIX_STRIP,
    _NUMBERED_SPLIT,
)
from app.presentation.executive_recommendation import parse_executive_recommendation
from app.presentation.executive_sanitize import (
    extract_recommendation_executive_text,
    sanitize_executive_text,
)
from app.ai_recommendations.risk_constants import (
    CATEGORY_LABEL_TO_CODE,
    MAX_RISK_RECOMMENDATION_ITEMS,
    MIN_RISK_RECOMMENDATION_ITEMS,
)

_CATEGORY_LINE = re.compile(r"^الفئة:\s*(.+)$", re.MULTILINE)
_ACTION_LINE = re.compile(r"^الإجراء المقترح:\s*(.+)$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class ParsedRiskRecommendationItem:
    index: int
    title: str
    description: str
    priority: str
    category_code: str | None


def parse_risk_mitigation_text(text: str) -> tuple[ParsedRiskRecommendationItem, ...]:
    cleaned = text.strip()
    if not cleaned:
        raise AiRecommendationError(
            "invalid_recommendation_count",
            "Risk mitigation options text is empty",
        )

    chunks = [
        chunk.strip()
        for chunk in _NUMBERED_SPLIT.split(cleaned)
        if chunk.strip()
    ]
    if not chunks:
        chunks = [cleaned]

    items: list[ParsedRiskRecommendationItem] = []
    for index, chunk in enumerate(chunks):
        body = _NUMBERED_PREFIX_STRIP.sub("", chunk).strip()
        if not body:
            raise AiRecommendationError(
                "missing_recommendation_title",
                "Risk recommendation item is empty",
                {"item_index": index},
            )
        category_code = _extract_category(body)
        if "المشكلة:" in body:
            fields = parse_executive_recommendation(body)
            title = fields.recommendation or fields.executive_decision
            description = fields.to_description()
            if not title:
                raise AiRecommendationError(
                    "missing_recommendation_title",
                    "Risk recommendation item missing action/title",
                    {"item_index": index},
                )
        else:
            action_match = _ACTION_LINE.search(body)
            if action_match:
                title = action_match.group(1).strip()
                description = body.strip()
            else:
                title, description = _split_title_and_description(body)
            if not title:
                raise AiRecommendationError(
                    "missing_recommendation_title",
                    "Risk recommendation item missing action/title",
                    {"item_index": index},
                )
            action, rationale = extract_recommendation_executive_text(body)
            if action:
                title = action[: MAX_TITLE_LENGTH - 3].rstrip() + "..." if len(action) > MAX_TITLE_LENGTH else action
            if rationale:
                description = rationale
        if len(title) > MAX_TITLE_LENGTH:
            title = title[: MAX_TITLE_LENGTH - 3].rstrip() + "..."
        title = sanitize_executive_text(title)
        description = sanitize_executive_text(description)
        items.append(
            ParsedRiskRecommendationItem(
                index=index,
                title=title,
                description=description or title,
                priority=_map_priority(body),
                category_code=category_code,
            )
        )

    if not MIN_RISK_RECOMMENDATION_ITEMS <= len(items) <= MAX_RISK_RECOMMENDATION_ITEMS:
        raise AiRecommendationError(
            "invalid_recommendation_count",
            "Risk recommendation count must be between 3 and 8",
            {"count": len(items)},
        )
    return tuple(items)


def _extract_category(body: str) -> str | None:
    match = _CATEGORY_LINE.search(body)
    if match is None:
        return None
    label = match.group(1).strip()
    for ar_label, code in CATEGORY_LABEL_TO_CODE.items():
        if ar_label in label:
            return code
    return None


def _split_title_and_description(body: str) -> tuple[str, str]:
    for separator in (". ", "\n"):
        if separator in body:
            head, _tail = body.split(separator, 1)
            return head.strip(), body.strip()
    return body.strip(), body.strip()
