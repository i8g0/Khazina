"""Human-readable Arabic evidence blocks for Facts Contract metrics."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal, InvalidOperation

from app.ai.prompts.facts import PromptFact
from app.ai.prompts.languages.pack import LanguagePack
from app.presentation.waste_category_labels import waste_category_label_ar

_DOMAIN_LABELS: dict[str, str] = {
    "waste": "الهدر المالي",
    "risk": "المخاطر",
    "scenario": "السيناريو",
}

_METRIC_LABELS: dict[str, str] = {
    "waste.total_amount": "إجمالي الهدر المالي",
    "waste.percentage": "نسبة الهدر من الإنفاق",
    "waste.top_category": "أعلى فئة هدر",
    "waste.top_category_percentage": "نسبة أعلى فئة من الهدر",
    "waste.potential_savings": "الوفورات المحتملة",
    "waste.savings_opportunity": "فرصة التوفير",
    "waste.savings_opportunities": "عدد فرص التوفير",
    "waste.overall_level": "مستوى الهدر العام",
    "waste.category_amount": "مبلغ الهدر في الفئة",
    "waste.category_percentage": "نسبة الفئة من إجمالي الهدر",
    "waste.category_level": "مستوى خطورة الفئة",
    "waste.reporting_period": "فترة التقرير",
    "waste.category_count": "عدد فئات الهدر",
    "waste.currency": "العملة",
    "waste.evidence_source": "مصدر الأدلة",
    "waste.financial_impact": "الأثر المالي",
    "risk.total_findings": "إجمالي النتائج",
    "risk.high_priority_count": "نتائج عالية الأولوية",
    "risk.medium_priority_count": "نتائج متوسطة الأولوية",
    "risk.low_priority_count": "نتائج منخفضة الأولوية",
    "risk.overall_posture_level": "وضع المخاطر العام",
    "risk.waste_percentage": "نسبة الهدر المرتبطة",
    "risk.category_count": "عدد فئات المخاطر",
    "risk.liquidity_ratio": "نسبة السيولة",
    "risk.score_max": "أعلى درجة مخاطرة",
    "risk.top_category": "أبرز فئة مخاطر",
    "scenario.archetype": "نوع السيناريو",
    "scenario.baseline_total": "إجمالي خط الأساس",
    "scenario.projected_total": "الإجمالي المتوقع",
    "scenario.delta_amount": "فرق المبلغ",
    "scenario.delta_percent": "نسبة التغير",
    "scenario.horizon_quarters": "أفق التوقع (ربع سنوي)",
    "scenario.confidence_percent": "نسبة الثقة",
    "scenario.category_baseline": "خط أساس الفئة",
    "scenario.category_projected": "توقع الفئة",
}

_SEVERITY_LABELS: dict[str, str] = {
    "high": "مرتفع",
    "medium": "متوسط",
    "low": "منخفض",
}

_PERIOD_LABELS: dict[str, str] = {
    "2026-Q1": "الربع الأول 2026",
    "2026-Q2": "الربع الثاني 2026",
    "2026-Q3": "الربع الثالث 2026",
    "2026-Q4": "الربع الرابع 2026",
}


def metric_label(metric: str) -> str:
    if metric in _METRIC_LABELS:
        return _METRIC_LABELS[metric]
    if metric.startswith("risk.finding."):
        return "درجة نتيجة مخاطرة"
    if metric.startswith("risk.category_count."):
        return "عدد نتائج الفئة"
    return metric.replace("_", " ").replace(".", " — ")


def domain_label(domain: str) -> str:
    return _DOMAIN_LABELS.get(domain, domain)


def format_period_label(period: str | None) -> str:
    if not period:
        return "الفترة غير محددة"
    return _PERIOD_LABELS.get(period, period.replace("-", " ").replace("Q", "الربع "))


def format_currency_ar(value: str) -> str:
    try:
        amount = Decimal(str(value).replace(",", ""))
    except InvalidOperation:
        return value
    if amount >= Decimal("1000000"):
        return f"{amount / Decimal('1000000'):,.2f} مليون ريال"
    return f"{amount:,.0f} ريال"


def format_percent_ar(value: str) -> str:
    try:
        pct = Decimal(str(value).replace(",", ""))
    except InvalidOperation:
        return value
    return f"{pct:.1f}%"


def format_fact_for_prompt(fact: PromptFact, pack: LanguagePack) -> str:
    """Render a single fact as executive evidence — no internal keys."""
    if fact.domain == "waste" and fact.metric.startswith("waste.category_"):
        return _format_waste_category_fact(fact)
    return _format_generic_fact(fact, pack)


def build_evidence_blocks(facts: Sequence[PromptFact], pack: LanguagePack) -> str:
    """Group waste facts into executive evidence blocks."""
    if not facts:
        return pack.no_facts_message

    waste_facts = [fact for fact in facts if fact.domain == "waste"]
    other_facts = [fact for fact in facts if fact.domain != "waste"]

    blocks: list[str] = []
    period = next((fact.period for fact in waste_facts if fact.period), None)
    if period:
        blocks.append(f"### فترة التقرير\n- {format_period_label(period)}")

    totals = [fact for fact in waste_facts if fact.metric in {
        "waste.total_amount",
        "waste.percentage",
        "waste.potential_savings",
        "waste.overall_level",
        "waste.top_category",
        "waste.top_category_percentage",
    }]
    if totals:
        blocks.append("### ملخص الهدر المالي")
        for fact in totals:
            blocks.append(format_fact_for_prompt(fact, pack))

    categories = _group_category_facts(waste_facts)
    if categories:
        blocks.append("### تفصيل الفئات (أدلة قابلة للاستشهاد)")
        for category_code, grouped in sorted(categories.items()):
            label = grouped.get("label") or waste_category_label_ar(category_code)
            amount = grouped.get("amount")
            percentage = grouped.get("percentage")
            level = grouped.get("level")
            lines = [f"- **{label}**"]
            if amount:
                lines.append(f"  - مبلغ الهدر: {format_currency_ar(amount)}")
            if percentage:
                lines.append(f"  - نسبة من إجمالي الهدر: {format_percent_ar(percentage)}")
            if level:
                sev = _SEVERITY_LABELS.get(level.lower(), level)
                lines.append(f"  - مستوى الخطورة: {sev}")
            blocks.append("\n".join(lines))

    for fact in other_facts:
        blocks.append(format_fact_for_prompt(fact, pack))

    return "\n\n".join(blocks) + "\n"


def _group_category_facts(facts: Sequence[PromptFact]) -> dict[str, dict[str, str]]:
    grouped: dict[str, dict[str, str]] = {}
    for fact in facts:
        category_name = (fact.metadata or {}).get("category_name")
        if not category_name:
            continue
        code = str(category_name)
        bucket = grouped.setdefault(code, {})
        label = (fact.metadata or {}).get("category_label_ar") or waste_category_label_ar(code)
        bucket["label"] = label
        if fact.metric == "waste.category_amount":
            bucket["amount"] = fact.value
        elif fact.metric == "waste.category_percentage":
            bucket["percentage"] = fact.value
        elif fact.metric == "waste.category_level":
            bucket["level"] = fact.value
    return grouped


def _format_waste_category_fact(fact: PromptFact) -> str:
    category_name = (fact.metadata or {}).get("category_name", "")
    label = (fact.metadata or {}).get("category_label_ar") or waste_category_label_ar(
        str(category_name)
    )
    period = format_period_label(fact.period)
    if fact.metric == "waste.category_amount":
        return (
            f"- خلال {period}، بلغ الهدر في فئة **{label}** "
            f"{format_currency_ar(fact.value)}."
        )
    if fact.metric == "waste.category_percentage":
        sev = ""
        if fact.severity:
            sev = f" (مستوى {_SEVERITY_LABELS.get(fact.severity.lower(), fact.severity)})"
        return (
            f"- تمثل فئة **{label}** {format_percent_ar(fact.value)} "
            f"من إجمالي الهدر{sev}."
        )
    if fact.metric == "waste.category_level":
        sev = _SEVERITY_LABELS.get(fact.value.lower(), fact.value)
        return f"- مستوى خطورة فئة **{label}**: {sev}."
    label_text = metric_label(fact.metric)
    return f"- {label_text}: {fact.value}"


def _format_generic_fact(fact: PromptFact, pack: LanguagePack) -> str:
    label = metric_label(fact.metric)
    period = format_period_label(fact.period) if fact.period else None

    if fact.metric == "waste.total_amount":
        line = f"- {label}: {format_currency_ar(fact.value)}"
    elif fact.metric in {"waste.potential_savings", "waste.savings_opportunity", "waste.financial_impact"}:
        line = f"- {label}: {format_currency_ar(fact.value)}"
    elif fact.unit == "percent":
        line = f"- {label}: {format_percent_ar(fact.value)}"
    elif fact.metric == "waste.top_category":
        category_label = (fact.metadata or {}).get("category_label_ar") or waste_category_label_ar(
            fact.value
        )
        line = f"- {label}: {category_label}"
    elif fact.metric == "waste.reporting_period":
        line = f"- {label}: {format_period_label(fact.value)}"
    elif fact.metric == "waste.currency":
        line = f"- العملة: ريال سعودي"
    elif fact.metric == "waste.evidence_source":
        line = f"- مصدر الأدلة: تحليل مالي حتمي ({fact.value})"
    else:
        line = f"- {label}: {fact.value}"

    if period and fact.metric not in {"waste.reporting_period"}:
        line = f"{line} (فترة: {period})"

    if fact.severity and fact.metric not in {"waste.category_percentage", "waste.category_level"}:
        sev = _SEVERITY_LABELS.get(fact.severity.lower(), fact.severity)
        line = f"{line} — مستوى الخطورة: {sev}"
    if fact.confidence:
        line = f"{line} — ثقة: {fact.confidence}"
    return line
