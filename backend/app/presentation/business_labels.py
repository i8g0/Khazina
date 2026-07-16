"""Centralized Arabic business labels — single source for categories, areas, and angles."""

from __future__ import annotations

import re

CATEGORY_LABELS_AR: dict[str, str] = {
    "overlapping_contracts": "العقود المتداخلة",
    "operations": "العمليات",
    "finance": "الشؤون المالية",
    "procurement": "المشتريات",
    "travel": "السفر والانتداب",
    "it": "تقنية المعلومات",
    "hr": "الموارد البشرية",
    "marketing": "التسويق",
    "compliance": "الامتثال",
    "administration": "الإدارة العامة",
    "facilities": "المرافق",
    "utilities": "المرافق العامة",
}

BUSINESS_AREA_AR: dict[str, str] = {
    "overlapping_contracts": "إدارة العقود والمشتريات",
    "operations": "التشغيل",
    "finance": "المالية والحوكمة",
    "procurement": "المشتريات",
    "travel": "الموارد البشرية",
    "it": "تقنية المعلومات",
    "hr": "الموارد البشرية",
    "marketing": "التسويق",
    "compliance": "الامتثال والحوكمة",
    "administration": "الإدارة العامة",
}

DEPARTMENT_HINTS_AR: dict[str, str] = {
    "finance": "الإدارة المالية",
    "procurement": "إدارة المشتريات",
    "operations": "إدارة العمليات",
    "overlapping_contracts": "إدارة العقود",
    "travel": "الموارد البشرية",
    "it": "تقنية المعلومات",
    "hr": "الموارد البشرية",
    "marketing": "التسويق",
    "compliance": "الامتثال",
}

RISK_POSTURE_AR: dict[str, str] = {
    "elevated": "مرتفع",
    "critical": "حرج",
    "moderate": "متوسط",
    "low": "منخفض",
}

RISK_PRIORITY_AR: dict[str, str] = {
    "high": "عالية",
    "medium": "متوسطة",
    "low": "منخفضة",
}

RISK_LEVEL_AR: dict[str, str] = {
    "high": "مرتفع",
    "medium": "متوسط",
    "low": "منخفض",
}

RISK_CATEGORY_AR: dict[str, str] = {
    "financial": "مخاطر مالية",
    "liquidity": "مخاطر السيولة",
    "operational": "مخاطر تشغيلية",
    "compliance": "مخاطر امتثال",
    "vendor": "مخاطر الموردين",
    "fraud": "مخاطر احتيال",
    "strategic": "مخاطر استراتيجية",
    "budget": "مخاطر الميزانية",
    "forecast": "مخاطر التوقعات",
}

EXECUTIVE_ANGLES_AR: tuple[str, ...] = (
    "الحوكمة المالية",
    "تحسين الموردين",
    "ضبط الميزانية",
    "الكفاءة التشغيلية",
    "الامتثال والمراقبة",
)

_ENGLISH_CATEGORY_TOKEN = re.compile(
    r"\b("
    r"finance|hr|marketing|operations|procurement|travel|it|compliance|"
    r"administration|facilities|utilities|overlapping_contracts"
    r")\b",
    re.IGNORECASE,
)


def risk_posture_ar(code: str) -> str:
    normalized = code.strip().lower()
    return RISK_POSTURE_AR.get(normalized, "متوسط")


def risk_priority_ar(code: str) -> str:
    normalized = code.strip().lower()
    return RISK_PRIORITY_AR.get(normalized, "متوسطة")


def risk_level_ar(code: str) -> str:
    normalized = code.strip().lower()
    return RISK_LEVEL_AR.get(normalized, "متوسط")


def risk_category_ar(code: str) -> str:
    normalized = code.strip().lower()
    if normalized in RISK_CATEGORY_AR:
        return RISK_CATEGORY_AR[normalized]
    return category_label_ar(code)


def category_label_ar(category_key: str) -> str:
    normalized = category_key.strip().lower()
    if normalized in CATEGORY_LABELS_AR:
        return CATEGORY_LABELS_AR[normalized]
    return category_key.replace("_", " ")


def business_area_ar(category_key: str) -> str:
    normalized = category_key.strip().lower()
    return BUSINESS_AREA_AR.get(normalized, category_label_ar(category_key))


def department_hint_ar(category_key: str) -> str | None:
    normalized = category_key.strip().lower()
    return DEPARTMENT_HINTS_AR.get(normalized)


def localize_category_tokens(text: str) -> str:
    """Replace English category codes with Arabic labels in executive text."""

    def _replace(match: re.Match[str]) -> str:
        return category_label_ar(match.group(0))

    return _ENGLISH_CATEGORY_TOKEN.sub(_replace, text)


def contains_english_category_leakage(text: str) -> bool:
    return bool(_ENGLISH_CATEGORY_TOKEN.search(text))


def assign_executive_angles(
    category_codes: list[str],
    *,
    count: int = 5,
) -> list[dict[str, str]]:
    """Deterministic angle + category assignment for recommendation diversity."""
    if not category_codes:
        category_codes = ["finance"]
    sorted_codes = sorted(set(category_codes))
    assignments: list[dict[str, str]] = []
    for index in range(count):
        code = sorted_codes[index % len(sorted_codes)]
        assignments.append(
            {
                "index": str(index + 1),
                "executive_angle": EXECUTIVE_ANGLES_AR[index % len(EXECUTIVE_ANGLES_AR)],
                "category_code": code,
                "category_label_ar": category_label_ar(code),
                "business_area_ar": business_area_ar(code),
                "department_hint_ar": department_hint_ar(code) or "غير محدد في البيانات",
            }
        )
    return assignments
