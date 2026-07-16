"""Deterministic section assemblers for report profiles."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.business.facts.contract import FactsContract
from app.presentation.business_labels import (
    business_area_ar,
    category_label_ar,
    risk_category_ar,
    risk_level_ar,
    risk_posture_ar,
    risk_priority_ar,
)
from app.presentation.executive_sanitize import sanitize_executive_text
from app.db.models import (
    Recommendation,
    Risk,
    RiskAnalysisResult,
    RiskFinding,
    RiskMitigationPlan,
    SimulationActionItem,
    SimulationAssumption,
    SimulationChartPoint,
    SimulationComparisonMetric,
    SimulationForecastSummary,
    SimulationImpactItem,
    SimulationRun,
    WasteAnalysisResult,
    WasteCategoryBreakdown,
    WasteVendorFinding,
)
from app.reports.constants import (
    PROFILE_RISK,
    PROFILE_SCENARIO,
    PROFILE_WASTE_DECISION,
    RISK_SECTION_ORDER,
    SCENARIO_SECTION_ORDER,
    WASTE_SECTION_ORDER,
)
from app.reports.content import ReportSection
from app.reports.loaders import (
    BaselineWasteContext,
    OrganizationContext,
    RiskReportInputs,
    ScenarioReportInputs,
    WasteReportInputs,
)


def _safe_float(value: Decimal | float | int | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _fact_dicts(facts: FactsContract) -> list[dict[str, Any]]:
    return [fact.to_dict() for fact in facts.facts]


def build_cover_section(
    *,
    context: OrganizationContext,
    run_title: str,
    completed_at: datetime | None,
    source_file_id: uuid.UUID | None,
    report_language: str | None = None,
    date_display_format: str | None = None,
    currency_display_code: str | None = None,
) -> ReportSection:
    payload: dict[str, Any] = {
        "organization_name": context.organization_name,
        "period_label": context.period_label,
        "run_title": run_title,
        "completed_at": completed_at.isoformat() if completed_at else None,
        "source_file_name": context.source_file_name,
        "source_file_id": str(source_file_id) if source_file_id else None,
    }
    if report_language is not None:
        payload["report_language"] = report_language
    if date_display_format is not None:
        payload["date_display_format"] = date_display_format
    if currency_display_code is not None:
        payload["currency_display_code"] = currency_display_code
    return ReportSection(key="cover", payload=payload)


def build_waste_executive_summary(
    inputs: WasteReportInputs,
    *,
    allow_ai: bool = True,
) -> ReportSection:
    if allow_ai and inputs.ai_insights and inputs.ai_insights.get("executive_summary"):
        text = sanitize_executive_text(
            str(inputs.ai_insights["executive_summary"]).strip()
        )
        source = "ai_insights"
    else:
        result = inputs.waste_result
        pct = _safe_float(result.waste_percentage) or 0.0
        total = _safe_float(result.total_waste_amount) or 0.0
        period = inputs.context.period_label or "الفترة الحالية"
        top = category_label_ar(result.top_category_name) if result.top_category_name else "غير محدد"
        savings = _safe_float(result.potential_savings_amount)
        text = (
            f"خلال {period}، سجّلت المؤسسة هدراً مالياً بنسبة {pct:.2f}% "
            f"بقيمة إجمالية {total:,.0f} ر.س. "
            f"أعلى ضغط مالي في {top}. "
        )
        if savings is not None:
            text += f"فرصة التوفير المقدرة {savings:,.0f} ر.س تتطلب قراراً تنفيذياً خلال 30 يوماً."
        else:
            text += "يُوصى بمراجعة فورية لأكبر بند إنفاق لحماية الربحية والسيولة."
        source = "facts_gold_fallback"
    return ReportSection(
        key="executive_summary",
        payload={"text": text, "source": source},
    )


def build_key_metrics_section(
    facts: FactsContract,
    headline: dict[str, Any] | None = None,
) -> ReportSection:
    payload: dict[str, Any] = {"facts": _fact_dicts(facts)}
    if headline:
        payload["headline"] = headline
    return ReportSection(key="key_metrics", payload=payload)


def build_waste_analysis_section(
    breakdowns: tuple[WasteCategoryBreakdown, ...],
    vendors: tuple[WasteVendorFinding, ...],
) -> ReportSection:
    ranked = sorted(breakdowns, key=lambda b: float(b.amount), reverse=True)
    return ReportSection(
        key="waste_analysis",
        payload={
            "category_breakdowns": [
                {
                    "category_name": b.category_name,
                    "category_label_ar": category_label_ar(b.category_name),
                    "business_area_ar": business_area_ar(b.category_name),
                    "amount": _safe_float(b.amount),
                    "percentage": _safe_float(b.percentage),
                    "department_id": str(b.department_id) if b.department_id else None,
                    "priority_rank": index + 1,
                }
                for index, b in enumerate(ranked)
            ],
            "executive_commentary": _waste_executive_commentary(ranked),
            "vendor_findings": [
                {
                    "vendor_name": v.vendor_name,
                    "amount": _safe_float(v.amount),
                    "deviation_label": v.deviation_label,
                    "category_label": v.category_label,
                    "status": v.status,
                }
                for v in vendors
            ],
        },
    )


def _waste_executive_commentary(
    breakdowns: tuple[WasteCategoryBreakdown, ...],
) -> str:
    if not breakdowns:
        return "لا تتوفر بيانات تفصيلية للهدر."
    top = breakdowns[0]
    label = category_label_ar(top.category_name)
    return (
        f"أولوية التدخل: فئة {label} بمبلغ {float(top.amount):,.0f} ريال "
        f"({float(top.percentage):.1f}% من إجمالي الهدر)."
    )


def build_decision_highlights_section(
    recommendations: tuple[Recommendation, ...],
) -> ReportSection:
    highlights: list[dict[str, Any]] = []
    for rec in recommendations[:5]:
        executive = (rec.source_context or {}).get("executive") or {}
        highlights.append(
            {
                "title": sanitize_executive_text(rec.title),
                "priority": rec.priority,
                "executive_angle": sanitize_executive_text(
                    str(executive.get("executive_angle", ""))
                ),
                "decision": sanitize_executive_text(
                    str(executive.get("executive_decision") or executive.get("recommendation") or rec.title)
                ),
                "expected_savings": sanitize_executive_text(
                    str(executive.get("expected_savings", ""))
                ),
            }
        )
    return ReportSection(key="decision_highlights", payload={"items": highlights})


def build_risk_explanation_section(ai_insights: dict[str, Any] | None) -> ReportSection | None:
    if not ai_insights or not ai_insights.get("risk_explanation"):
        return None
    return ReportSection(
        key="risk_explanation",
        payload={"text": sanitize_executive_text(str(ai_insights["risk_explanation"]).strip())},
    )


def build_recommendations_section(
    recommendations: tuple[Recommendation, ...],
) -> ReportSection:
    return ReportSection(
        key="recommendations",
        payload={
            "items": [
                {
                    "title": rec.title,
                    "description": rec.description,
                    "priority": rec.priority,
                    "confidence_label": rec.confidence_label,
                    "estimated_savings_amount": _safe_float(rec.estimated_savings_amount),
                    "source_context": dict(rec.source_context or {}),
                }
                for rec in recommendations
            ]
        },
    )


def build_waste_provenance_section(
    inputs: WasteReportInputs,
    *,
    ai_insights_consumed: bool,
) -> ReportSection:
    run = inputs.run
    facts = inputs.facts
    ai_meta: dict[str, Any] = {}
    if inputs.ai_insights:
        for key in (
            "generated_at",
            "model",
            "prompt_version",
            "tasks_executed",
            "source_snapshot_id",
        ):
            if key in inputs.ai_insights:
                ai_meta[key] = inputs.ai_insights[key]
    return ReportSection(
        key="provenance",
        payload={
            "source_snapshot_id": str(run.source_snapshot_id)
            if run.source_snapshot_id
            else None,
            "facts_contract_version": facts.contract_version,
            "engine_id": facts.engine_id,
            "engine_version": facts.engine_version,
            "ai_insights_consumed": ai_insights_consumed,
            "ai_metadata": ai_meta,
            "profile": PROFILE_WASTE_DECISION,
        },
    )


def assemble_waste_sections(
    inputs: WasteReportInputs,
    *,
    include_ai_sections: bool = True,
    include_recommendations: bool = True,
    report_language: str | None = None,
    date_display_format: str | None = None,
    currency_display_code: str | None = None,
) -> tuple[ReportSection, ...]:
    ai_consumed = bool(
        include_ai_sections
        and inputs.ai_insights
        and inputs.ai_insights.get("executive_summary")
    )
    headline = {
        "total_waste_amount": _safe_float(inputs.waste_result.total_waste_amount),
        "waste_percentage": _safe_float(inputs.waste_result.waste_percentage),
        "potential_savings_amount": _safe_float(
            inputs.waste_result.potential_savings_amount
        ),
        "active_savings_opportunities": inputs.waste_result.active_savings_opportunities,
    }
    sections: list[ReportSection] = [
        build_cover_section(
            context=inputs.context,
            run_title=inputs.run.title,
            completed_at=inputs.run.completed_at,
            source_file_id=inputs.run.source_file_id,
            report_language=report_language,
            date_display_format=date_display_format,
            currency_display_code=currency_display_code,
        ),
        build_waste_executive_summary(inputs, allow_ai=include_ai_sections),
        build_decision_highlights_section(inputs.recommendations),
        build_key_metrics_section(inputs.facts, headline=headline),
        build_waste_analysis_section(inputs.category_breakdowns, inputs.vendor_findings),
    ]
    if include_recommendations:
        sections.append(build_recommendations_section(inputs.recommendations))
    sections.append(build_waste_provenance_section(inputs, ai_insights_consumed=ai_consumed))
    if include_ai_sections:
        risk = build_risk_explanation_section(inputs.ai_insights)
        if risk is not None:
            sections.insert(4, risk)
    order = {key: index for index, key in enumerate(WASTE_SECTION_ORDER)}
    sections.sort(key=lambda s: order.get(s.key, 999))
    return tuple(sections)


def build_scenario_executive_summary(
    simulation_run: SimulationRun,
    forecast: SimulationForecastSummary,
) -> ReportSection:
    title = simulation_run.result_title or "نتائج المحاكاة"
    description = simulation_run.result_description or ""
    delta = forecast.delta_value
    text = f"{title}. {description} {forecast.delta_label}: {delta}.".strip()
    return ReportSection(
        key="executive_summary",
        payload={"text": text, "source": "simulation_gold"},
    )


def build_scenario_overview_section(
    inputs: ScenarioReportInputs,
) -> ReportSection:
    provenance = inputs.scenario_provenance
    return ReportSection(
        key="scenario_overview",
        payload={
            "scenario_id": str(inputs.scenario.id),
            "scenario_name": inputs.scenario.name,
            "archetype": provenance.get("archetype"),
            "assumptions_count": len(inputs.assumptions),
            "assumptions": [
                {"label": a.label, "value": a.value} for a in inputs.assumptions
            ],
        },
    )


def build_forecast_and_delta_section(
    forecast: SimulationForecastSummary,
    chart_points: tuple[SimulationChartPoint, ...],
    comparison_metrics: tuple[SimulationComparisonMetric, ...],
) -> ReportSection:
    return ReportSection(
        key="forecast_and_delta",
        payload={
            "forecast_summary": {
                "baseline_label": forecast.baseline_label,
                "baseline_value": forecast.baseline_value,
                "projected_label": forecast.projected_label,
                "projected_value": forecast.projected_value,
                "delta_label": forecast.delta_label,
                "delta_value": forecast.delta_value,
                "confidence_label": forecast.confidence_label,
            },
            "chart_points": [
                {
                    "quarter_label": p.quarter_label,
                    "quarter_order": p.quarter_order,
                    "baseline_amount": _safe_float(p.baseline_amount),
                    "projected_amount": _safe_float(p.projected_amount),
                }
                for p in chart_points
            ],
            "comparison_metrics": [
                {
                    "metric_name": m.metric_name,
                    "current_value": m.current_value,
                    "simulated_value": m.simulated_value,
                    "change_value": m.change_value,
                    "direction": m.direction,
                }
                for m in comparison_metrics
            ],
        },
    )


def build_impact_and_actions_section(
    impact_items: tuple[SimulationImpactItem, ...],
    action_items: tuple[SimulationActionItem, ...],
) -> ReportSection:
    return ReportSection(
        key="impact_and_actions",
        payload={
            "impact_items": [
                {
                    "category_label": item.category_label,
                    "baseline_value": item.baseline_value,
                    "projected_value": item.projected_value,
                    "change_value": item.change_value,
                    "direction": item.direction,
                }
                for item in impact_items
            ],
            "action_items": [
                {
                    "title": item.title,
                    "description": item.description,
                    "status": item.status,
                }
                for item in action_items
            ],
        },
    )


def build_baseline_context_section(
    baseline: BaselineWasteContext | None,
    baseline_run_id: str | None,
) -> ReportSection | None:
    if baseline is None:
        return None
    ai_summary: str | None = None
    if baseline.ai_insights and baseline.ai_insights.get("executive_summary"):
        ai_summary = str(baseline.ai_insights["executive_summary"]).strip()
    return ReportSection(
        key="baseline_context",
        payload={
            "baseline_analysis_run_id": baseline_run_id,
            "waste_summary": {
                "total_waste_amount": _safe_float(baseline.waste_result.total_waste_amount),
                "waste_percentage": _safe_float(baseline.waste_result.waste_percentage),
                "potential_savings_amount": _safe_float(
                    baseline.waste_result.potential_savings_amount
                ),
            },
            "category_breakdowns": [
                {
                    "category_name": b.category_name,
                    "amount": _safe_float(b.amount),
                    "percentage": _safe_float(b.percentage),
                }
                for b in baseline.category_breakdowns
            ],
            "ai_executive_summary": ai_summary,
        },
    )


def build_scenario_provenance_section(inputs: ScenarioReportInputs) -> ReportSection:
    run = inputs.run
    facts = inputs.facts
    provenance = dict(inputs.scenario_provenance)
    return ReportSection(
        key="provenance",
        payload={
            "scenario_provenance": provenance,
            "source_snapshot_id": str(run.source_snapshot_id)
            if run.source_snapshot_id
            else None,
            "facts_contract_version": facts.contract_version,
            "engine_id": facts.engine_id,
            "engine_version": facts.engine_version,
            "profile": PROFILE_SCENARIO,
        },
    )


def assemble_scenario_sections(
    inputs: ScenarioReportInputs,
    *,
    include_scenario_provenance: bool = True,
    include_ai_sections: bool = True,
    report_language: str | None = None,
    date_display_format: str | None = None,
    currency_display_code: str | None = None,
) -> tuple[ReportSection, ...]:
    baseline_run_id = inputs.scenario_provenance.get("baseline_analysis_run_id")
    baseline_run_id_str = str(baseline_run_id) if baseline_run_id else None
    sections: list[ReportSection] = [
        build_cover_section(
            context=inputs.context,
            run_title=inputs.run.title,
            completed_at=inputs.run.completed_at,
            source_file_id=inputs.run.source_file_id,
            report_language=report_language,
            date_display_format=date_display_format,
            currency_display_code=currency_display_code,
        ),
        build_scenario_executive_summary(inputs.simulation_run, inputs.forecast_summary),
        build_scenario_overview_section(inputs),
        build_forecast_and_delta_section(
            inputs.forecast_summary,
            inputs.chart_points,
            inputs.comparison_metrics,
        ),
        build_impact_and_actions_section(inputs.impact_items, inputs.action_items),
        build_key_metrics_section(inputs.facts),
    ]
    if include_scenario_provenance:
        sections.append(build_scenario_provenance_section(inputs))
    baseline_section = None
    if include_ai_sections:
        baseline_section = build_baseline_context_section(
            inputs.baseline, baseline_run_id_str
        )
    if baseline_section is not None:
        sections.insert(6, baseline_section)
    order = {key: index for index, key in enumerate(SCENARIO_SECTION_ORDER)}
    sections.sort(key=lambda s: order.get(s.key, 999))
    return tuple(sections)


def build_risk_executive_summary(
    inputs: RiskReportInputs,
    *,
    allow_ai: bool = True,
) -> ReportSection:
    if (
        allow_ai
        and inputs.ai_insights
        and inputs.ai_insights.get("risk_executive_summary")
    ):
        text = str(inputs.ai_insights["risk_executive_summary"]).strip()
        source = "ai_insights"
    else:
        result = inputs.risk_result
        posture = risk_posture_ar(result.overall_posture_level)
        text = (
            f"تحليل المخاطر المالية: الوضع العام {posture}. "
            f"إجمالي النتائج {result.total_findings} "
            f"(عالية: {result.high_priority_count}, "
            f"متوسطة: {result.medium_priority_count}, "
            f"منخفضة: {result.low_priority_count})."
        )
        source = "risk_gold_fallback"
    return ReportSection(
        key="executive_summary",
        payload={"text": text, "source": source},
    )


def build_risk_summary_section(result: RiskAnalysisResult) -> ReportSection:
    return ReportSection(
        key="risk_summary",
        payload={
            "overall_posture_level": risk_posture_ar(result.overall_posture_level),
            "total_findings": result.total_findings,
            "high_priority_count": result.high_priority_count,
            "medium_priority_count": result.medium_priority_count,
            "low_priority_count": result.low_priority_count,
            "top_category": risk_category_ar(result.top_category_code or ""),
        },
    )


def _finding_evidence(finding: RiskFinding) -> dict[str, Any]:
    return finding.evidence if isinstance(finding.evidence, dict) else {}


def _finding_exposure_sar(finding: RiskFinding) -> Decimal:
    evidence = _finding_evidence(finding)
    raw = evidence.get("amount_exposed_sar")
    if raw is None:
        return Decimal("0")
    try:
        return Decimal(str(raw))
    except Exception:
        return Decimal("0")


def build_current_situation_section(inputs: RiskReportInputs) -> ReportSection:
    result = inputs.risk_result
    posture = risk_posture_ar(result.overall_posture_level)
    departments: list[str] = []
    for finding in inputs.findings:
        evidence = _finding_evidence(finding)
        dept = str(evidence.get("department_ar") or "").strip()
        if dept and dept != "—" and dept not in departments:
            departments.append(dept)
    dept_phrase = ""
    if departments:
        dept_phrase = f" الإدارات الأكثر تعرضاً: {', '.join(departments[:5])}."
    text = sanitize_executive_text(
        f"الوضع الحالي {posture}: {result.total_findings} مخاطر مكتشفة "
        f"({result.high_priority_count} عالية الأولوية).{dept_phrase}"
    )
    return ReportSection(key="current_situation", payload={"text": text})


def build_financial_impact_section(inputs: RiskReportInputs) -> ReportSection:
    total_exposure = sum(_finding_exposure_sar(f) for f in inputs.findings)
    from app.business.engines.risk.rules.ar import format_sar

    items: list[dict[str, Any]] = []
    for finding in sorted(inputs.findings, key=lambda f: -f.score)[:10]:
        evidence = _finding_evidence(finding)
        items.append(
            {
                "title": sanitize_executive_text(finding.name),
                "exposure": str(evidence.get("amount_exposed_label") or "—"),
                "savings": str(evidence.get("estimated_savings_label") or "—"),
                "priority": risk_priority_ar(finding.priority),
                "department": str(evidence.get("department_ar") or "—"),
            }
        )
    summary = (
        f"إجمالي التعرّض المالي المقدّر {format_sar(float(total_exposure))} "
        f"عبر {len(inputs.findings)} مخاطر."
        if total_exposure > 0
        else "التعرّض المالي محسوب من بيانات التحليل الحالي."
    )
    return ReportSection(
        key="financial_impact",
        payload={"summary": summary, "items": items},
    )


def build_operational_impact_section(inputs: RiskReportInputs) -> ReportSection:
    items: list[dict[str, str]] = []
    for finding in sorted(inputs.findings, key=lambda f: -f.score)[:10]:
        evidence = _finding_evidence(finding)
        impact = str(
            evidence.get("business_impact_ar")
            or evidence.get("if_ignored_ar")
            or finding.description
        )
        items.append(
            {
                "title": sanitize_executive_text(finding.name),
                "department": str(evidence.get("department_ar") or "—"),
                "supplier": str(evidence.get("supplier_ar") or "—"),
                "impact": sanitize_executive_text(impact),
            }
        )
    return ReportSection(key="operational_impact", payload={"items": items})


def build_evidence_section(inputs: RiskReportInputs) -> ReportSection:
    items: list[dict[str, str]] = []
    for finding in sorted(inputs.findings, key=lambda f: -f.score)[:12]:
        evidence = _finding_evidence(finding)
        items.append(
            {
                "title": sanitize_executive_text(finding.name),
                "detection_reason": sanitize_executive_text(
                    str(evidence.get("detection_reason_ar") or finding.description)
                ),
                "data_source": str(evidence.get("data_source_ar") or "الملف المرفوع"),
                "department": str(evidence.get("department_ar") or "—"),
                "supplier": str(evidence.get("supplier_ar") or "—"),
                "exposure": str(evidence.get("amount_exposed_label") or "—"),
                "waste": str(evidence.get("waste_value_label") or "—"),
                "confidence": str(evidence.get("confidence_score") or "—"),
            }
        )
    return ReportSection(key="evidence", payload={"items": items})


def build_proposed_decisions_section(
    recommendations: tuple[Recommendation, ...],
) -> ReportSection:
    items: list[dict[str, str]] = []
    for rec in recommendations[:10]:
        items.append(
            {
                "title": sanitize_executive_text(rec.title),
                "description": sanitize_executive_text(rec.description),
                "priority": risk_priority_ar(rec.priority),
            }
        )
    return ReportSection(key="proposed_decisions", payload={"items": items})


def build_next_steps_section(inputs: RiskReportInputs) -> ReportSection:
    steps: list[str] = []
    for finding in sorted(inputs.findings, key=lambda f: -f.score)[:5]:
        evidence = _finding_evidence(finding)
        action = str(evidence.get("recommended_action_ar") or "").strip()
        owner = str(evidence.get("owner_ar") or "").strip()
        timeline = str(evidence.get("target_timeline_ar") or "").strip()
        if action:
            step = action
            if owner and owner != "—":
                step += f" — المسؤول: {owner}"
            if timeline and timeline != "—":
                step += f" — {timeline}"
            steps.append(sanitize_executive_text(step))
    if not steps and inputs.recommendations:
        for rec in inputs.recommendations[:5]:
            steps.append(sanitize_executive_text(rec.title))
    return ReportSection(key="next_steps", payload={"items": steps})


def build_top_risks_section(findings: tuple[RiskFinding, ...]) -> ReportSection:
    ordered = sorted(
        findings,
        key=lambda f: (-f.score, f.priority),
    )[:10]
    return ReportSection(
        key="top_risks",
        payload={
            "items": [
                {
                    "name": sanitize_executive_text(f.name),
                    "category": risk_category_ar(f.category_code),
                    "score": f.score,
                    "priority": risk_priority_ar(f.priority),
                    "likelihood": risk_level_ar(f.likelihood),
                    "impact": risk_level_ar(f.impact),
                    "status": f.finding_status,
                    "department": str(_finding_evidence(f).get("department_ar") or "—"),
                    "supplier": str(_finding_evidence(f).get("supplier_ar") or "—"),
                    "exposure": str(_finding_evidence(f).get("amount_exposed_label") or "—"),
                    "description": sanitize_executive_text(f.description),
                }
                for f in ordered
            ]
        },
    )


def build_mitigation_status_section(
    plans: tuple[RiskMitigationPlan, ...],
    register_risks: tuple[Risk, ...],
) -> ReportSection:
    risk_ids = {r.id for r in register_risks}
    related = [p for p in plans if p.risk_id in risk_ids]
    by_status: dict[str, int] = {}
    for plan in related:
        by_status[plan.status] = by_status.get(plan.status, 0) + 1
    return ReportSection(
        key="mitigation_status",
        payload={
            "total_plans": len(related),
            "by_status": by_status,
            "plans": [
                {
                    "title": p.title,
                    "status": p.status,
                    "target_date": p.target_date.isoformat(),
                    "risk_id": str(p.risk_id),
                }
                for p in related[:20]
            ],
        },
    )


def build_register_statistics_section(
    register_risks: tuple[Risk, ...],
    findings: tuple[RiskFinding, ...],
) -> ReportSection:
    by_lifecycle: dict[str, int] = {}
    for risk in register_risks:
        key = risk.lifecycle_status or risk.status
        by_lifecycle[key] = by_lifecycle.get(key, 0) + 1
    promoted = sum(1 for f in findings if f.finding_status == "promoted")
    return ReportSection(
        key="register_statistics",
        payload={
            "register_count": len(register_risks),
            "promoted_findings": promoted,
            "by_lifecycle": by_lifecycle,
            "items": [
                {
                    "name": r.name,
                    "priority": r.priority,
                    "score": r.score,
                    "lifecycle_status": r.lifecycle_status,
                    "status": r.status,
                }
                for r in register_risks[:20]
            ],
        },
    )


def build_risk_provenance_section(
    inputs: RiskReportInputs,
    *,
    ai_insights_consumed: bool,
) -> ReportSection:
    run = inputs.run
    facts = inputs.facts
    ai_meta: dict[str, Any] = {}
    if inputs.ai_insights:
        for key in (
            "generated_at",
            "model",
            "prompt_version",
            "tasks_executed",
            "traceability",
            "domain",
        ):
            if key in inputs.ai_insights:
                ai_meta[key] = inputs.ai_insights[key]
    return ReportSection(
        key="provenance",
        payload={
            "source_snapshot_id": str(run.source_snapshot_id)
            if run.source_snapshot_id
            else None,
            "facts_contract_version": facts.contract_version,
            "engine_id": facts.engine_id,
            "engine_version": facts.engine_version,
            "ai_insights_consumed": ai_insights_consumed,
            "ai_metadata": ai_meta,
            "profile": PROFILE_RISK,
        },
    )


def assemble_risk_sections(
    inputs: RiskReportInputs,
    *,
    include_ai_sections: bool = True,
    include_recommendations: bool = True,
    report_language: str | None = None,
    date_display_format: str | None = None,
    currency_display_code: str | None = None,
) -> tuple[ReportSection, ...]:
    ai_consumed = bool(
        include_ai_sections
        and inputs.ai_insights
        and inputs.ai_insights.get("risk_executive_summary")
    )
    headline = {
        "overall_posture_level": inputs.risk_result.overall_posture_level,
        "total_findings": inputs.risk_result.total_findings,
        "high_priority_count": inputs.risk_result.high_priority_count,
    }
    sections: list[ReportSection] = [
        build_cover_section(
            context=inputs.context,
            run_title=inputs.run.title,
            completed_at=inputs.run.completed_at,
            source_file_id=inputs.run.source_file_id,
            report_language=report_language,
            date_display_format=date_display_format,
            currency_display_code=currency_display_code,
        ),
        build_risk_executive_summary(inputs, allow_ai=include_ai_sections),
        build_current_situation_section(inputs),
        build_key_metrics_section(inputs.facts, headline=headline),
        build_risk_summary_section(inputs.risk_result),
        build_top_risks_section(inputs.findings),
        build_financial_impact_section(inputs),
        build_operational_impact_section(inputs),
        build_evidence_section(inputs),
        build_mitigation_status_section(
            inputs.mitigation_plans, inputs.register_risks
        ),
        build_register_statistics_section(inputs.register_risks, inputs.findings),
    ]
    if include_recommendations and inputs.recommendations:
        sections.append(build_recommendations_section(inputs.recommendations))
        sections.append(build_proposed_decisions_section(inputs.recommendations))
    sections.append(build_next_steps_section(inputs))
    sections.append(
        build_risk_provenance_section(inputs, ai_insights_consumed=ai_consumed)
    )
    order = {key: index for index, key in enumerate(RISK_SECTION_ORDER)}
    sections.sort(key=lambda s: order.get(s.key, 999))
    return tuple(sections)


def derive_department_id(
    breakdowns: tuple[WasteCategoryBreakdown, ...],
) -> uuid.UUID | None:
    if not breakdowns:
        return None
    dominant = max(breakdowns, key=lambda b: float(b.amount))
    return dominant.department_id
