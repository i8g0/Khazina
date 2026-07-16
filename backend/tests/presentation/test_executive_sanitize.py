"""Tests for executive presentation sanitizer."""

from __future__ import annotations

from app.presentation.executive_sanitize import (
    contains_technical_leakage,
    extract_recommendation_executive_text,
    sanitize_executive_text,
)


def test_sanitize_removes_dot_notation_keys() -> None:
    raw = "تشير البيانات إلى waste.top_category في Finance"
    cleaned = sanitize_executive_text(raw)
    assert "waste.top_category" not in cleaned
    assert not contains_technical_leakage(cleaned)


def test_sanitize_removes_reference_facts_block() -> None:
    raw = (
        "الإجراء المقترح:\nمراجعة العقود\n"
        "المبرر:\nتخفيض التكلفة\n"
        "الحقائق المرجعية:\nwaste.category_level، waste.top_category"
    )
    action, rationale = extract_recommendation_executive_text(raw)
    assert "waste." not in action
    assert "waste." not in rationale
    assert "الحقائق المرجعية" not in rationale


def test_sanitize_removes_forbidden_literals() -> None:
    raw = "facts_contract_version: 1.0 metadata engine_id waste-engine"
    cleaned = sanitize_executive_text(raw)
    assert "facts_contract" not in cleaned.lower()
    assert "metadata" not in cleaned.lower()
    assert "engine_id" not in cleaned.lower()


def test_extract_recommendation_keeps_executive_parts_only() -> None:
    body = (
        "الإجراء المقترح:\n"
        "تعزيز مراجعة المصروفات المالية\n"
        "المبرر:\n"
        "يتركز الهدر في هذه الفئة ويتطلب ضوابط رقابية."
    )
    action, rationale = extract_recommendation_executive_text(body)
    assert "مراجعة" in action
    assert "الهدر" in rationale
