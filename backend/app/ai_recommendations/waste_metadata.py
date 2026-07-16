"""Build deterministic waste metadata supplement for prompts (Sprint 3/4)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.business.facts.contract import FactsContract
from app.presentation.business_labels import assign_executive_angles, category_label_ar
from app.presentation.evidence_block import evidence_block_from_breakdown
from app.presentation.metric_labels import format_currency_ar, format_period_label, format_percent_ar
from app.presentation.waste_category_labels import waste_category_owner_hint


def build_waste_metadata_supplement(
    runtime_metadata: dict[str, Any],
    *,
    facts_contract: FactsContract | None = None,
    gold_breakdowns: list[Any] | None = None,
    gold_vendors: list[Any] | None = None,
    department_names: dict[str, str] | None = None,
) -> str:
    """Format waste Gold context, evidence blocks, and mandatory angles for prompts."""
    context = runtime_metadata.get("waste_gold_context") or {}
    if not isinstance(context, dict):
        context = {}

    lines = ["## سياق الأعمال الحتمي", ""]

    org_name = context.get("organization_name")
    period_label = context.get("reporting_period_label")
    if not period_label and facts_contract:
        period_label = _period_from_contract(facts_contract)
    period_display = format_period_label(str(period_label)) if period_label else None

    if org_name:
        lines.append(f"### المنظمة\n- {org_name}")
    if period_display:
        lines.append(f"### فترة التقرير\n- {period_display}")

    lines.extend(["", "### ملخص مالي"])
    total = context.get("total_waste_amount")
    waste_pct = context.get("waste_percentage")
    savings = context.get("potential_savings_amount")
    if total is not None:
        lines.append(f"- إجمالي الهدر: {format_currency_ar(str(total))}")
    if waste_pct is not None:
        lines.append(f"- نسبة الهدر: {format_percent_ar(str(waste_pct))}")
    if savings is not None:
        lines.append(f"- الوفورات المحتملة: {format_currency_ar(str(savings))}")

    breakdowns = _resolve_breakdowns(context, gold_breakdowns, facts_contract)
    category_codes = [str(b.get("category_name", "")) for b in breakdowns if b.get("category_name")]

    if breakdowns:
        lines.extend(["", "### تفصيل الفئات (بالعربية فقط)", ""])
        for item in breakdowns[:10]:
            code = str(item.get("category_name", ""))
            label = item.get("category_label_ar") or category_label_ar(code)
            dept_id = item.get("department_id")
            dept_name = None
            if dept_id and department_names:
                dept_name = department_names.get(str(dept_id))
            owner = dept_name or waste_category_owner_hint(code) or "غير محدد في البيانات"
            item = {**item, "department_name": owner, "category_label_ar": label}
            lines.append(evidence_block_from_breakdown(item, period=str(period_label)))
            lines.append("")

    angles = assign_executive_angles(category_codes, count=5)
    lines.extend(["", "### الزوايا التنفيذية الإلزامية (5 توصيات — بدون تكرار)", ""])
    for assignment in angles:
        lines.append(
            f"توصية {assignment['index']}: {assignment['executive_angle']} — "
            f"الفئة: {assignment['category_label_ar']} — "
            f"مجال الأعمال: {assignment['business_area_ar']} — "
            f"الإدارة: {assignment['department_hint_ar']}"
        )

    vendors = context.get("vendor_findings") or []
    if not vendors and gold_vendors:
        vendors = [
            {
                "vendor_name": getattr(item, "vendor_name", ""),
                "amount": float(getattr(item, "amount", 0)),
            }
            for item in gold_vendors
        ]
    if vendors:
        lines.extend(["", "### أبرز الموردين", ""])
        for item in vendors[:5]:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- {item.get('vendor_name', '—')}: "
                f"{format_currency_ar(str(item.get('amount', 0)))}"
            )

    unavailable = [
        "الفاتورة (غير متوفر في البيانات المالية)",
        "مركز التكلفة (غير متوفر)",
        "وحدة الأعمال (غير متوفر)",
        "مالك الميزانية (غير متوفر)",
        "أكبر المعاملات (غير متوفر)",
    ]
    lines.extend(
        [
            "",
            "### حقول غير متوفرة — اذكرها صراحةً عند الحاجة",
            *[f"- {field}" for field in unavailable],
            "",
            "### قواعد صارمة",
            "- استخدم أسماء الفئات بالعربية فقط — ممنوع finance/hr/marketing/operations.",
            "- كل توصية: زاوية مختلفة + دليل منظم + قرار تنفيذي + لماذا الأولوية.",
            "- ممنوع: هناك فئة، بعض الفئات، يُوصى بشكل عام، قد يساعد، ربما.",
            "- إذا غاب حقل، اكتب: غير متوفر في البيانات — [اسم الحقل].",
            "",
        ]
    )
    return "\n".join(lines)


def _resolve_breakdowns(
    context: dict[str, Any],
    gold_breakdowns: list[Any] | None,
    facts_contract: FactsContract | None,
) -> list[dict[str, Any]]:
    breakdowns = context.get("category_breakdowns") or []
    if not breakdowns and gold_breakdowns:
        breakdowns = [
            {
                "category_name": getattr(item, "category_name", ""),
                "amount": float(getattr(item, "amount", 0)),
                "percentage": float(getattr(item, "percentage", 0)),
                "department_id": (
                    str(getattr(item, "department_id"))
                    if getattr(item, "department_id", None)
                    else None
                ),
            }
            for item in gold_breakdowns
        ]
    if not breakdowns and facts_contract:
        breakdowns = _breakdowns_from_contract(facts_contract)
    enriched: list[dict[str, Any]] = []
    for item in breakdowns:
        if not isinstance(item, dict):
            continue
        code = str(item.get("category_name", ""))
        enriched.append(
            {
                **item,
                "category_label_ar": item.get("category_label_ar")
                or category_label_ar(code),
            }
        )
    return enriched


def _period_from_contract(contract: FactsContract) -> str | None:
    for fact in contract.facts:
        if fact.metric == "waste.reporting_period":
            return fact.value
        if fact.period:
            return fact.period
    executive = (contract.extensions or {}).get("executive_context") or {}
    return executive.get("reporting_period_label")


def _breakdowns_from_contract(contract: FactsContract) -> list[dict[str, Any]]:
    amounts = {
        (fact.metadata or {}).get("category_name"): fact.value
        for fact in contract.facts
        if fact.metric == "waste.category_amount"
    }
    percentages = {
        (fact.metadata or {}).get("category_name"): fact.value
        for fact in contract.facts
        if fact.metric == "waste.category_percentage"
    }
    breakdowns: list[dict[str, Any]] = []
    for code, amount in amounts.items():
        if not code:
            continue
        breakdowns.append(
            {
                "category_name": code,
                "category_label_ar": category_label_ar(str(code)),
                "amount": float(Decimal(str(amount))),
                "percentage": float(Decimal(str(percentages.get(code, "0")))),
            }
        )
    return breakdowns
