"""Structured executive evidence blocks — deterministic formatting."""

from __future__ import annotations

from app.presentation.business_labels import business_area_ar, category_label_ar
from app.presentation.metric_labels import format_currency_ar, format_period_label, format_percent_ar


def format_evidence_block(
    *,
    category_code: str,
    period: str | None,
    amount: str | float | None,
    percentage: str | float | None,
    department: str | None = None,
    financial_impact: str | float | None = None,
) -> str:
    """Render the mandatory الدليل block for recommendations."""
    label = category_label_ar(category_code)
    area = business_area_ar(category_code)
    dept = department or "غير محدد في البيانات"
    period_text = format_period_label(period) if period else "غير متوفر في البيانات"
    amount_text = format_currency_ar(str(amount)) if amount is not None else "غير متوفر في البيانات"
    pct_text = format_percent_ar(str(percentage)) if percentage is not None else "غير متوفر في البيانات"
    impact_text = (
        format_currency_ar(str(financial_impact))
        if financial_impact is not None
        else amount_text
    )
    return (
        f"الدليل:\n"
        f"الفئة: {label}\n"
        f"مجال الأعمال: {area}\n"
        f"الإدارة: {dept}\n"
        f"الفترة: {period_text}\n"
        f"قيمة الهدر: {amount_text}\n"
        f"النسبة: {pct_text}\n"
        f"الأثر المالي: {impact_text}"
    )


def evidence_block_from_breakdown(
    item: dict[str, str | float | None],
    *,
    period: str | None,
    department: str | None = None,
) -> str:
    code = str(item.get("category_name", ""))
    return format_evidence_block(
        category_code=code,
        period=period,
        amount=item.get("amount"),
        percentage=item.get("percentage"),
        department=department or item.get("department_name"),
        financial_impact=item.get("amount"),
    )
