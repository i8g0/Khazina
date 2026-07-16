"""Arabic executive labels for risk findings (Sprint 7)."""

from __future__ import annotations

CATEGORY_DEPARTMENT_AR: dict[str, str] = {
    "finance": "الشؤون المالية",
    "procurement": "المشتريات",
    "overlapping_contracts": "العقود والموردين",
    "operations": "العمليات",
    "it": "تقنية المعلومات",
    "logistics": "اللوجستيات والنقل",
    "hr": "الموارد البشرية",
    "legal": "الشؤون القانونية",
    "travel": "السفر والضيافة",
    "marketing": "التسويق",
    "compliance": "الامتثال",
    "administration": "الإدارة العامة",
    "facilities": "المرافق",
    "utilities": "المرافق والخدمات",
}

CATEGORY_LABEL_AR: dict[str, str] = {
    "financial": "مخاطر مالية",
    "liquidity": "مخاطر السيولة",
    "operational": "مخاطر تشغيلية",
    "compliance": "مخاطر الامتثال",
    "vendor": "مخاطر الموردين",
    "fraud": "مخاطر الاحتيال",
    "budget": "مخاطر الموازنة",
    "strategic": "مخاطر استراتيجية",
    "forecast": "مخاطر التوقعات",
}

LEVEL_AR: dict[str, str] = {
    "low": "منخفض",
    "medium": "متوسط",
    "high": "مرتفع",
}

PRIORITY_OWNER: dict[str, str] = {
    "high": "المدير المالي",
    "medium": "مدير الإدارة المعنية",
    "low": "مشرف العمليات المالية",
}

PRIORITY_TIMELINE: dict[str, str] = {
    "high": "30 يوماً",
    "medium": "60 يوماً",
    "low": "90 يوماً",
}


def department_for_category(category_key: str | None) -> str:
    if not category_key:
        return "غير محدد"
    normalized = category_key.strip().lower().replace(" ", "_")
    return CATEGORY_DEPARTMENT_AR.get(normalized, category_key)


def format_sar(amount: float | str) -> str:
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return str(amount)
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f} مليون ر.س"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f} ألف ر.س"
    return f"{value:,.0f} ر.س"
