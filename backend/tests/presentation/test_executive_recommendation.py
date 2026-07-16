"""Tests for executive recommendation parsing."""

from __future__ import annotations

from app.presentation.executive_recommendation import parse_executive_recommendation


def test_parse_full_executive_recommendation_v3() -> None:
    body = (
        "المشكلة:\n"
        "تركز الهدر في الشؤون المالية.\n"
        "الأدلة:\n"
        "خلال الربع الثاني 2026 بلغ الهدر 1,075,000 ريال (45.9%).\n"
        "الأثر على الأعمال:\n"
        "ضغط على الهامش التشغيلي.\n"
        "السبب الجذري:\n"
        "غير متوفر في البيانات.\n"
        "التوصية التنفيذية:\n"
        "إطلاق مبادرة حوكمة مالية شاملة\n"
        "الأولوية:\n"
        "عالية\n"
        "المسؤول:\n"
        "الشؤون المالية\n"
        "الإطار الزمني:\n"
        "30–45 يوماً\n"
        "الوفورات المتوقعة:\n"
        "1.2 مليون ر.س\n"
        "مؤشر النجاح:\n"
        "خفض الهدر 10% خلال 90 يوماً"
    )
    fields = parse_executive_recommendation(body)
    assert "حوكمة" in fields.recommendation
    assert fields.evidence
    assert fields.business_impact
    assert "1.2" in fields.expected_savings
    assert fields.owner_department


def test_parse_legacy_action_format() -> None:
    body = (
        "الإجراء:\n"
        "إطلاق مبادرة حوكمة مالية شاملة\n"
        "لماذا:\n"
        "يتركز الهدر في الشؤون المالية\n"
        "الأثر على الأعمال:\n"
        "تحسين الهامش\n"
        "الوفورات المتوقعة:\n"
        "1,075,000 ريال\n"
        "الأولوية:\n"
        "عالية\n"
        "المدة الزمنية:\n"
        "30–45 يوماً\n"
        "الإدارة المسؤولة:\n"
        "الشؤون المالية"
    )
    fields = parse_executive_recommendation(body)
    assert "حوكمة" in fields.recommendation
    assert fields.why
