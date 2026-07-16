"""Executive Financial Judgment Layer — materiality, realism, and CFO verdict (deterministic)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.business.engines.scenario.calculator import ScenarioCalculationResult
from app.business.engines.scenario.input import ScenarioBaselineInput
from app.presentation.business_labels import category_label_ar
from app.scenario.ai_contract import (
    ExecutiveJudgmentPayload,
    FinancialRealityPayload,
    InterpretedScenario,
    ScenarioAction,
)

RecommendationType = Literal[
    "approve",
    "approve_with_modifications",
    "postpone",
    "reject",
]

RECOMMENDATION_LABELS_AR: dict[RecommendationType, str] = {
    "approve": "الموافقة",
    "approve_with_modifications": "الموافقة مع تعديلات",
    "postpone": "التأجيل",
    "reject": "الرفض",
}

MATERIALITY_IMMATERIAL_PCT = 0.5
MATERIALITY_MARGINAL_PCT = 2.0
MATERIALITY_MATERIAL_PCT = 10.0

MIN_BRANCH_BUDGET_LARGE_CO = 2_000_000.0
MIN_BRANCH_BUDGET_MEDIUM_CO = 500_000.0
MIN_BRANCH_BUDGET_SMALL_CO = 100_000.0

SCALE_SMALL_MAX = 10_000_000.0
SCALE_MEDIUM_MAX = 100_000_000.0


@dataclass(frozen=True, slots=True)
class _ActionContext:
    requested_amount: float
    reference_amount: float
    reference_label_ar: str
    pct_of_reference: float
    pct_of_total_spend: float
    action_type: str
    category_key: str | None


def build_executive_judgment(
    *,
    user_request: str,
    interpreted: InterpretedScenario,
    baseline: ScenarioBaselineInput,
    calculation: ScenarioCalculationResult,
    financial_reality: FinancialRealityPayload | None = None,
) -> ExecutiveJudgmentPayload:
    """Deterministic senior-consultant judgment grounded in uploaded baseline."""
    total_spend = float(baseline.total_baseline)
    scale_label = _scale_label_ar(total_spend)
    ctx = _extract_action_context(interpreted, baseline, total_spend)

    materiality = _materiality_narrative(ctx, total_spend)
    realism = _realism_narrative(user_request, ctx, total_spend, interpreted, scale_label)
    scale_comparison = _scale_comparison_narrative(ctx, total_spend, baseline, calculation)
    strategic = _strategic_advice(ctx, total_spend)
    rec_type, rec_rationale = _recommendation(
        user_request, ctx, total_spend, interpreted, financial_reality, realism
    )
    rec_label = RECOMMENDATION_LABELS_AR[rec_type]

    indicators = _supporting_indicators(ctx, total_spend, calculation, financial_reality)
    assumptions = _assumptions_list(ctx, baseline, financial_reality)
    risks = _remaining_risks(ctx, financial_reality)
    confidence = _confidence_statement(financial_reality, ctx, total_spend)

    financial_reasoning = (
        f"{materiality} {realism} "
        f"المؤشرات الداعمة: {'؛ '.join(indicators[:4])}."
    ).strip()

    verdict = _verdict_summary(rec_label, ctx, materiality)
    justification = (
        f"بناءً على إجمالي إنفاق {total_spend:,.0f} ر.س ({scale_label})، "
        f"المبلغ المطلوب {ctx.requested_amount:,.0f} ر.س يمثل {ctx.pct_of_reference:.3f}% "
        f"من {ctx.reference_label_ar}."
    )
    alternative = strategic
    if "بدلاً من" in strategic:
        alternative = strategic.split("بدلاً من", 1)[1].strip()
    next_step = _next_step(rec_type, rec_label, ctx)

    return ExecutiveJudgmentPayload(
        materiality_analysis=materiality,
        financial_realism=realism,
        scale_comparison=scale_comparison,
        strategic_advice=strategic,
        recommendation=rec_label,
        recommendation_type=rec_type,
        recommendation_rationale=rec_rationale,
        financial_reasoning=financial_reasoning,
        supporting_indicators=indicators,
        assumptions_used=assumptions,
        remaining_risks=risks,
        executive_verdict=verdict,
        financial_justification=justification,
        strategic_recommendation=f"{rec_label}: {rec_rationale}",
        confidence_statement=confidence,
        alternative_option=alternative,
        next_step=next_step,
    )


def merge_explanation_judgment(
    explanation_dict: dict,
    judgment: ExecutiveJudgmentPayload,
) -> dict:
    """Ensure AI explanation includes executive judgment; deterministic fields win on conflict."""
    merged = dict(explanation_dict)
    j = judgment.model_dump(mode="json")
    ej = merged.get("executive_judgment")
    if not isinstance(ej, dict):
        merged["executive_judgment"] = j
    else:
        for key, value in j.items():
            if key not in ej or not ej[key]:
                ej[key] = value
        merged["executive_judgment"] = ej

    if not merged.get("board_recommendation"):
        merged["board_recommendation"] = judgment.strategic_recommendation
    if not merged.get("confidence"):
        merged["confidence"] = judgment.confidence_statement
    return merged


def _extract_action_context(
    interpreted: InterpretedScenario,
    baseline: ScenarioBaselineInput,
    total_spend: float,
) -> _ActionContext:
    primary = interpreted.actions[0] if interpreted.actions else ScenarioAction(
        action_type="operational_change", description=""
    )
    amount = _resolve_requested_amount(primary, interpreted, total_spend)
    category_key, ref_amount, ref_label = _resolve_reference_baseline(primary, baseline, total_spend)
    pct_ref = (amount / ref_amount * 100) if ref_amount > 0 else 0.0
    pct_total = (amount / total_spend * 100) if total_spend > 0 else 0.0
    return _ActionContext(
        requested_amount=amount,
        reference_amount=ref_amount,
        reference_label_ar=ref_label,
        pct_of_reference=pct_ref,
        pct_of_total_spend=pct_total,
        action_type=primary.action_type,
        category_key=category_key,
    )


def _resolve_requested_amount(
    action: ScenarioAction,
    interpreted: InterpretedScenario,
    total_spend: float,
) -> float:
    if interpreted.target_amount is not None and interpreted.target_amount > 0:
        return float(interpreted.target_amount)
    if action.mode == "absolute":
        if action.amount is not None and action.amount > 0:
            return float(action.amount)
        if action.value is not None and action.value > 0:
            return float(action.value)
    if action.mode == "percent" and action.value is not None:
        return total_spend * (float(action.value) / 100.0)
    if action.mode == "count" and action.value is not None:
        unit = float(action.amount or 85_000)
        return unit * float(action.value)
    return 0.0


def _resolve_reference_baseline(
    action: ScenarioAction,
    baseline: ScenarioBaselineInput,
    total_spend: float,
) -> tuple[str | None, float, str]:
    needle = (action.category or action.department or "").strip().lower()
    categories = {c.category_name: float(c.amount) for c in baseline.categories}
    if needle:
        for key, amount in categories.items():
            if needle in key.lower() or key.lower() in needle:
                return key, amount, f"ميزانية {category_label_ar(key)}"
        for key, amount in categories.items():
            label = category_label_ar(key)
            if needle in label or label in needle:
                return key, amount, f"ميزانية {label}"
    if categories:
        dominant = max(categories.items(), key=lambda x: x[1])
        return dominant[0], dominant[1], f"ميزانية {category_label_ar(dominant[0])}"
    return None, total_spend, "إجمالي الإنفاق التشغيلي"


def _materiality_tier(pct: float) -> str:
    if pct < MATERIALITY_IMMATERIAL_PCT:
        return "غير جوهري"
    if pct < MATERIALITY_MARGINAL_PCT:
        return "هامشي"
    if pct < MATERIALITY_MATERIAL_PCT:
        return "جوهري"
    return "استراتيجي"


def _materiality_narrative(ctx: _ActionContext, total_spend: float) -> str:
    tier = _materiality_tier(ctx.pct_of_reference)
    if ctx.requested_amount <= 0:
        return (
            "لم يُحدد مبلغ صريح في الطلب — "
            "البيانات المالية المتاحة لا تكفي لتقدير الأثر المالي بدقة."
        )
    base = (
        f"المبلغ المطلوب {ctx.requested_amount:,.0f} ر.س يمثل "
        f"{ctx.pct_of_reference:.3f}% من {ctx.reference_label_ar} "
        f"({ctx.reference_amount:,.0f} ر.س) و{ctx.pct_of_total_spend:.3f}% من إجمالي الإنفاق "
        f"({total_spend:,.0f} ر.س). التصنيف: {tier}."
    )
    if ctx.pct_of_reference < MATERIALITY_IMMATERIAL_PCT:
        base += (
            " من غير المرجّح أن يحقق هذا الاستثمار وحده أثراً مالياً قابلاً للقياس "
            "خلال فترة التقرير الحالية."
        )
    elif ctx.pct_of_reference < MATERIALITY_MARGINAL_PCT:
        base += " الأثر محتمل لكن محدود — يتطلب مؤشرات أداء واضحة للمتابعة."
    else:
        base += " التغيير جوهري نسبياً ويستحق قراراً مجلسياً."
    return base


def _realism_narrative(
    user_request: str,
    ctx: _ActionContext,
    total_spend: float,
    interpreted: InterpretedScenario,
    scale_label: str,
) -> str:
    at = ctx.action_type
    amount = ctx.requested_amount
    combined = f"{user_request} {interpreted.title_ar} {interpreted.summary_ar}".lower()
    branch_keywords = ("فرع", "branch", "تأسيس", "افتتاح")
    is_branch = any(kw in combined for kw in branch_keywords) or at == "investment"

    if is_branch and amount > 0:
        min_budget = _min_branch_budget(total_spend)
        if amount < min_budget:
            return (
                f"الميزانية المقترحة ({amount:,.0f} ر.س) غير كافية لتأسيس وتشغيل فرع "
                f"بمقياس المنشأة ({scale_label}، إنفاق سنوي {total_spend:,.0f} ر.س). "
                f"المبلغ يمثل {ctx.pct_of_total_spend:.3f}% فقط من الإنفاق التشغيلي السنوي — "
                f"السيناريو غير قابل للتنفيذ مالياً بالميزانية الحالية."
            )

    if amount > 0 and ctx.pct_of_total_spend > 35:
        return (
            f"الزيادة المطلوبة ({amount:,.0f} ر.س) تمثل {ctx.pct_of_total_spend:.1f}% "
            f"من الإنفاق — يتجاوز حدود المرونة التشغيلية المعتادة ويتطلب خطة تمويل."
        )

    if amount <= 0:
        return "لم يُحدد مبلغ كافٍ لتقييم واقعية التنفيذ — يلزم توضيح الميزانية."

    return (
        f"الطلب ماليّاً مقبولاً ضمن نطاق {scale_label} "
        f"({ctx.pct_of_total_spend:.3f}% من الإنفاق التشغيلي)."
    )


def _min_branch_budget(total_spend: float) -> float:
    if total_spend >= SCALE_MEDIUM_MAX:
        return MIN_BRANCH_BUDGET_LARGE_CO
    if total_spend >= SCALE_SMALL_MAX:
        return MIN_BRANCH_BUDGET_MEDIUM_CO
    return MIN_BRANCH_BUDGET_SMALL_CO


def _scale_label_ar(total_spend: float) -> str:
    if total_spend >= SCALE_MEDIUM_MAX:
        return "منشأة كبيرة"
    if total_spend >= SCALE_SMALL_MAX:
        return "منشأة متوسطة"
    return "منشأة صغيرة"


def _scale_comparison_narrative(
    ctx: _ActionContext,
    total_spend: float,
    baseline: ScenarioBaselineInput,
    calculation: ScenarioCalculationResult,
) -> str:
    implied_revenue = total_spend * 1.05
    lines = [
        f"إجمالي الإنفاق التشغيلي: {total_spend:,.0f} ر.س.",
        f"الإيرادات التقديرية (افتراض: 105% من الإنفاق): {implied_revenue:,.0f} ر.س.",
        f"{ctx.reference_label_ar}: {ctx.reference_amount:,.0f} ر.س.",
        f"أثر المحاكاة على الإنفاق: {calculation.delta_percent:+.2f}% "
        f"({calculation.delta_amount:+,.0f} ر.س).",
    ]
    if len(baseline.categories) > 1:
        top3 = sorted(baseline.categories, key=lambda c: c.amount, reverse=True)[:3]
        dept_line = "، ".join(
            f"{category_label_ar(c.category_name)} {c.amount:,.0f} ر.س" for c in top3
        )
        lines.append(f"أكبر بنود الإنفاق: {dept_line}.")
    return " ".join(lines)


def _strategic_advice(ctx: _ActionContext, total_spend: float) -> str:
    amount = ctx.requested_amount
    if amount <= 0:
        return "حدّد ميزانية واضحة ونسبة مستهدفة قبل اتخاذ قرار مجلسي."

    if ctx.pct_of_reference < MATERIALITY_IMMATERIAL_PCT:
        min_material = ctx.reference_amount * (MATERIALITY_MARGINAL_PCT / 100.0)
        return (
            f"بدلاً من زيادة {ctx.reference_label_ar} بـ {amount:,.0f} ر.س فقط، "
            f"فكّر في إعادة توجيه الإنفاق من حملات/بنود ضعيفة الأداء، "
            f"أو رفع الميزانية بنسبة 2–5% ({min_material:,.0f}–"
            f"{ctx.reference_amount * 0.05:,.0f} ر.س) لتحقيق أثر تجاري قابل للقياس."
        )

    if ctx.action_type in {"investment", "operational_change"}:
        return (
            f"إن وُجدت مبررات استراتيجية، اربط الاستثمار {amount:,.0f} ر.س "
            f"بمؤشرات نجاح ربعية وحدّ أقصى للانحراف عن الميزانية."
        )

    return (
        f"راجع توزيع الإنفاق بين الفئات قبل التوسع — "
        f"الهدف {amount:,.0f} ر.س يمثل {ctx.pct_of_reference:.2f}% من {ctx.reference_label_ar}."
    )


def _recommendation(
    _user_request: str,
    ctx: _ActionContext,
    total_spend: float,
    interpreted: InterpretedScenario,
    financial_reality: FinancialRealityPayload | None,
    realism: str,
) -> tuple[RecommendationType, str]:
    unrealistic = "غير قابل للتنفيذ" in realism or "غير كافية" in realism
    low_confidence = financial_reality is not None and financial_reality.confidence_score < 50
    immaterial = ctx.pct_of_reference < MATERIALITY_IMMATERIAL_PCT and ctx.requested_amount > 0

    if unrealistic:
        return (
            "reject",
            f"الميزانية ({ctx.requested_amount:,.0f} ر.س) لا تتوافق مع مقياس المنشأة "
            f"({total_spend:,.0f} ر.س إنفاق سنوي) — يتعذّر التنفيذ دون تعديل جوهري.",
        )
    if low_confidence and ctx.requested_amount <= 0:
        return (
            "postpone",
            "البيانات المالية المتاحة لا تكفي لتقدير السيناريو بثقة عالية — "
            "يُفضّل استكمال البيانات قبل القرار.",
        )
    if immaterial:
        return (
            "approve_with_modifications",
            f"الأثر المالي غير جوهري ({ctx.pct_of_reference:.3f}% من {ctx.reference_label_ar}) — "
            f"الموافقة مشروطة بربط الإنفاق بمؤشرات أداء أو برفع المبلغ إلى نطاق 2–5%.",
        )
    if ctx.pct_of_reference >= MATERIALITY_MATERIAL_PCT:
        return (
            "approve_with_modifications",
            f"تغيير استراتيجي ({ctx.pct_of_reference:.1f}% من {ctx.reference_label_ar}) — "
            f"الموافقة مشروطة بخطة تنفيذ ومراقبة مالية ربعية.",
        )
    return (
        "approve",
        f"الطلب متناسب مع مقياس المنشأة ({ctx.pct_of_total_spend:.2f}% من الإنفاق) "
        f"ومبرر مالياً ضمن نطاق المحاكاة.",
    )


def _supporting_indicators(
    ctx: _ActionContext,
    total_spend: float,
    calculation: ScenarioCalculationResult,
    financial_reality: FinancialRealityPayload | None,
) -> list[str]:
    items = [
        f"إجمالي الإنفاق: {total_spend:,.0f} ر.س",
        f"{ctx.reference_label_ar}: {ctx.reference_amount:,.0f} ر.س",
        f"نسبة الطلب من المرجع: {ctx.pct_of_reference:.3f}%",
        f"تغير الإنفاق المتوقع: {calculation.delta_percent:+.2f}%",
    ]
    if financial_reality:
        items.append(
            f"ثقة المحاكاة: {financial_reality.confidence_score}/100 "
            f"({financial_reality.confidence_level})"
        )
        ec = financial_reality.expense_change
        items.append(
            f"نطاق تغير الإنفاق: {ec.expected:+,.0f} ر.س (أسوأ {ec.worst:+,.0f} / أفضل {ec.best:+,.0f})"
        )
    return items


def _assumptions_list(
    ctx: _ActionContext,
    baseline: ScenarioBaselineInput,
    financial_reality: FinancialRealityPayload | None,
) -> list[str]:
    assumptions = [
        f"خط الأساس من البيانات المرفوعة ({baseline.source_dataset}).",
        "الإيرادات التقديرية = 105% من إجمالي الإنفاق (افتراض صريح).",
    ]
    if financial_reality and financial_reality.assumptions_used:
        assumptions.extend(financial_reality.assumptions_used[:5])
    if ctx.requested_amount <= 0:
        assumptions.append("المبلغ المطلوب غير محدد — تقديرات الأثر مقيّدة.")
    return assumptions


def _remaining_risks(
    ctx: _ActionContext,
    financial_reality: FinancialRealityPayload | None,
) -> str:
    parts: list[str] = []
    if ctx.pct_of_reference < MATERIALITY_IMMATERIAL_PCT:
        parts.append("أثر غير قابل للقياس خلال الفترة الحالية.")
    if financial_reality and financial_reality.validation_notes:
        parts.extend(financial_reality.validation_notes[:3])
    if not parts:
        parts.append("مخاطر تنفيذ وانحراف عن الميزانية — تتطلب متابعة ربعية.")
    return " ".join(parts)


def _confidence_statement(
    financial_reality: FinancialRealityPayload | None,
    ctx: _ActionContext,
    total_spend: float,
) -> str:
    if ctx.requested_amount <= 0:
        return (
            "البيانات المالية المتاحة غير كافية لتقدير هذا السيناريو بثقة عالية — "
            "يُوصى بتحديد المبلغ والفترة بدقة."
        )
    if financial_reality:
        level_ar = {"high": "عالية", "medium": "متوسطة", "low": "منخفضة"}.get(
            financial_reality.confidence_level, "متوسطة"
        )
        return (
            f"ثقة {level_ar} ({financial_reality.confidence_score}/100): "
            f"{financial_reality.confidence_rationale}"
        )
    return f"ثقة متوسطة — مبنية على إنفاق أساس {total_spend:,.0f} ر.س من البيانات المرفوعة."


def _verdict_summary(rec_label: str, ctx: _ActionContext, materiality: str) -> str:
    snippet = materiality if len(materiality) <= 160 else f"{materiality[:157]}…"
    return f"الحكم التنفيذي: {rec_label}. المبلغ {ctx.requested_amount:,.0f} ر.س — {snippet}"


def _next_step(rec_type: RecommendationType, rec_label: str, ctx: _ActionContext) -> str:
    if rec_type == "reject":
        return "إعادة صياغة السيناريو بميزانية متناسبة مع مقياس المنشأة أو إلغاء الطلب."
    if rec_type == "postpone":
        return "استكمال البيانات المالية وتحديد الميزانية قبل عرض القرار على المجلس."
    if rec_type == "approve_with_modifications":
        return (
            f"اعتماد {rec_label} مع تحديد مؤشرات نجاح وربط {ctx.requested_amount:,.0f} ر.س "
            f"بخطة تنفيذ ربعية."
        )
    return "اعتماد التوصية وإدراجها في خطة الإنفاق القادمة مع متابعة شهرية."
