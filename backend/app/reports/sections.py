"""Deterministic section assemblers for report profiles."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.business.facts.contract import FactsContract
from app.db.models import (
    Recommendation,
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
    PROFILE_SCENARIO,
    PROFILE_WASTE_DECISION,
    SCENARIO_SECTION_ORDER,
    WASTE_SECTION_ORDER,
)
from app.reports.content import ReportSection
from app.reports.loaders import (
    BaselineWasteContext,
    OrganizationContext,
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
        text = str(inputs.ai_insights["executive_summary"]).strip()
        source = "ai_insights"
    else:
        result = inputs.waste_result
        parts = [
            f"تحليل الهدر المالي: نسبة الهدر {_safe_float(result.waste_percentage):.2f}%",
            f"بإجمالي {_safe_float(result.total_waste_amount):,.2f}",
        ]
        if result.top_category_name:
            parts.append(f"أعلى فئة: {result.top_category_name}")
        if result.potential_savings_amount is not None:
            parts.append(
                f"وفورات محتملة: {_safe_float(result.potential_savings_amount):,.2f}"
            )
        text = ". ".join(parts) + "."
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
    return ReportSection(
        key="waste_analysis",
        payload={
            "category_breakdowns": [
                {
                    "category_name": b.category_name,
                    "amount": _safe_float(b.amount),
                    "percentage": _safe_float(b.percentage),
                    "department_id": str(b.department_id) if b.department_id else None,
                }
                for b in breakdowns
            ],
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


def build_risk_explanation_section(ai_insights: dict[str, Any] | None) -> ReportSection | None:
    if not ai_insights or not ai_insights.get("risk_explanation"):
        return None
    return ReportSection(
        key="risk_explanation",
        payload={"text": str(ai_insights["risk_explanation"]).strip()},
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


def derive_department_id(
    breakdowns: tuple[WasteCategoryBreakdown, ...],
) -> uuid.UUID | None:
    if not breakdowns:
        return None
    dominant = max(breakdowns, key=lambda b: float(b.amount))
    return dominant.department_id
