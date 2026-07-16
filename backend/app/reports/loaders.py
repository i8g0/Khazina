"""Read-only input loaders for report generation."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.business.facts.contract import FactsContract
from app.db.models import (
    AnalysisRun,
    Organization,
    Recommendation,
    ReportingPeriod,
    SimulationActionItem,
    SimulationAssumption,
    SimulationChartPoint,
    SimulationComparisonMetric,
    SimulationForecastSummary,
    SimulationImpactItem,
    SimulationRun,
    SimulationScenario,
    WasteAnalysisResult,
    WasteCategoryBreakdown,
    WasteVendorFinding,
)
from app.db.models.enums import AnalysisRunStatus, AnalysisType, RecommendationDomain
from app.db.models.repository import FinancialFile
from app.reports.exceptions import ReportBuilderError
from app.reports.facts_loader import load_facts_contract
from app.repositories import (
    AnalysisRepository,
    FinancialRepository,
    OrganizationRepository,
    RecommendationRepository,
    SimulationRepository,
    WasteRepository,
)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


@dataclass(frozen=True, slots=True)
class OrganizationContext:
    organization_id: uuid.UUID
    organization_name: str
    period_label: str | None
    source_file_name: str | None


@dataclass(frozen=True, slots=True)
class WasteReportInputs:
    run: AnalysisRun
    facts: FactsContract
    waste_result: WasteAnalysisResult
    category_breakdowns: tuple[WasteCategoryBreakdown, ...]
    vendor_findings: tuple[WasteVendorFinding, ...]
    recommendations: tuple[Recommendation, ...]
    ai_insights: dict[str, Any] | None
    context: OrganizationContext


@dataclass(frozen=True, slots=True)
class BaselineWasteContext:
    waste_result: WasteAnalysisResult
    category_breakdowns: tuple[WasteCategoryBreakdown, ...]
    ai_insights: dict[str, Any] | None


@dataclass(frozen=True, slots=True)
class ScenarioReportInputs:
    run: AnalysisRun
    facts: FactsContract
    simulation_run: SimulationRun
    scenario: SimulationScenario
    assumptions: tuple[SimulationAssumption, ...]
    forecast_summary: SimulationForecastSummary
    chart_points: tuple[SimulationChartPoint, ...]
    comparison_metrics: tuple[SimulationComparisonMetric, ...]
    impact_items: tuple[SimulationImpactItem, ...]
    action_items: tuple[SimulationActionItem, ...]
    scenario_provenance: dict[str, Any]
    baseline: BaselineWasteContext | None
    context: OrganizationContext


class ReportInputLoader:
    """Loads persisted artifacts for report profiles — read-only."""

    def __init__(
        self,
        analysis_repository: AnalysisRepository,
        waste_repository: WasteRepository,
        simulation_repository: SimulationRepository,
        recommendation_repository: RecommendationRepository,
        organization_repository: OrganizationRepository,
        financial_repository: FinancialRepository,
    ) -> None:
        self._analyses = analysis_repository
        self._waste = waste_repository
        self._simulations = simulation_repository
        self._recommendations = recommendation_repository
        self._organizations = organization_repository
        self._financials = financial_repository

    def load_waste_inputs(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        run: AnalysisRun | None = None,
    ) -> WasteReportInputs:
        if run is not None:
            if run.id != analysis_run_id or run.organization_id != organization_id:
                raise ReportBuilderError(
                    "analysis_run_not_found",
                    f"Analysis run '{analysis_run_id}' not found",
                )
            if run.status != AnalysisRunStatus.COMPLETED:
                raise ReportBuilderError(
                    "analysis_run_not_completed",
                    f"Analysis run must be completed (current status: '{run.status}')",
                )
            resolved_run = run
        else:
            resolved_run = self._require_completed_run(organization_id, analysis_run_id)
        if resolved_run.analysis_type != AnalysisType.FINANCIAL_WASTE:
            raise ReportBuilderError(
                "unsupported_analysis_type",
                f"Analysis type '{run.analysis_type}' is not supported for waste reports",
            )
        metadata = dict(resolved_run.runtime_metadata or {})
        facts = load_facts_contract(metadata)
        waste_result = self._waste.get_result_for_run(resolved_run.id)
        if waste_result is None:
            raise ReportBuilderError(
                "missing_waste_gold",
                "Analysis run has no waste_analysis_results Gold record",
            )
        breakdowns = tuple(self._waste.list_category_breakdowns(resolved_run.id))
        vendors = tuple(self._waste.list_vendor_findings(resolved_run.id))
        recommendations = tuple(
            rec
            for rec in self._recommendations.list_for_analysis_run(resolved_run.id)
            if rec.domain_source == RecommendationDomain.WASTE
        )
        ai_insights = metadata.get("ai_insights")
        if ai_insights is not None and not isinstance(ai_insights, dict):
            ai_insights = None
        context = self._load_context(organization_id, resolved_run)
        return WasteReportInputs(
            run=resolved_run,
            facts=facts,
            waste_result=waste_result,
            category_breakdowns=breakdowns,
            vendor_findings=vendors,
            recommendations=recommendations,
            ai_insights=ai_insights,
            context=context,
        )

    def load_scenario_inputs(
        self, organization_id: uuid.UUID, analysis_run_id: uuid.UUID
    ) -> ScenarioReportInputs:
        run = self._require_completed_run(organization_id, analysis_run_id)
        if run.analysis_type != AnalysisType.SIMULATION:
            raise ReportBuilderError(
                "unsupported_analysis_type",
                f"Analysis type '{run.analysis_type}' is not supported for scenario reports",
            )
        metadata = dict(run.runtime_metadata or {})
        facts = load_facts_contract(metadata)
        provenance = metadata.get("scenario_provenance")
        if not isinstance(provenance, dict):
            raise ReportBuilderError(
                "missing_scenario_provenance",
                "Analysis run runtime_metadata.scenario_provenance is missing or invalid",
            )
        simulation_run = self._simulations.get_run_for_analysis_run(run.id)
        if simulation_run is None:
            raise ReportBuilderError(
                "missing_simulation_run",
                "Analysis run has no simulation_runs Gold record",
            )
        forecast = self._simulations.get_forecast_summary(simulation_run.id)
        if forecast is None:
            raise ReportBuilderError(
                "incomplete_simulation_gold",
                "Simulation run is missing forecast summary",
            )
        chart_points = tuple(self._simulations.list_chart_points(simulation_run.id))
        if not chart_points:
            raise ReportBuilderError(
                "incomplete_simulation_gold",
                "Simulation run is missing chart points",
            )
        comparison_metrics = tuple(
            self._simulations.list_comparison_metrics(simulation_run.id)
        )
        if not comparison_metrics:
            raise ReportBuilderError(
                "incomplete_simulation_gold",
                "Simulation run is missing comparison metrics",
            )
        impact_items = tuple(self._simulations.list_impact_items(simulation_run.id))
        if not impact_items:
            raise ReportBuilderError(
                "incomplete_simulation_gold",
                "Simulation run is missing impact items",
            )
        action_items = tuple(self._simulations.list_action_items(simulation_run.id))
        if not action_items:
            raise ReportBuilderError(
                "incomplete_simulation_gold",
                "Simulation run is missing action items",
            )
        scenario = self._simulations.get_scenario(simulation_run.scenario_id)
        if scenario is None:
            raise ReportBuilderError(
                "missing_scenario",
                "Simulation scenario not found for run",
            )
        assumptions = tuple(self._simulations.list_assumptions(scenario.id))
        baseline = self._load_baseline(organization_id, provenance)
        context = self._load_context(organization_id, run)
        return ScenarioReportInputs(
            run=run,
            facts=facts,
            simulation_run=simulation_run,
            scenario=scenario,
            assumptions=assumptions,
            forecast_summary=forecast,
            chart_points=chart_points,
            comparison_metrics=comparison_metrics,
            impact_items=impact_items,
            action_items=action_items,
            scenario_provenance=provenance,
            baseline=baseline,
            context=context,
        )

    def _require_completed_run(
        self, organization_id: uuid.UUID, analysis_run_id: uuid.UUID
    ) -> AnalysisRun:
        run = self._analyses.get(analysis_run_id)
        if run is None:
            raise ReportBuilderError(
                "analysis_run_not_found",
                f"Analysis run '{analysis_run_id}' not found",
            )
        if run.organization_id != organization_id:
            raise ReportBuilderError(
                "analysis_run_not_found",
                f"Analysis run '{analysis_run_id}' not found",
            )
        if run.status != AnalysisRunStatus.COMPLETED:
            raise ReportBuilderError(
                "analysis_run_not_completed",
                f"Analysis run must be completed (current status: '{run.status}')",
            )
        return run

    def _load_context(
        self, organization_id: uuid.UUID, run: AnalysisRun
    ) -> OrganizationContext:
        org = self._organizations.get_organization(organization_id)
        org_name = org.name if isinstance(org, Organization) else str(organization_id)
        period_label: str | None = None
        if run.reporting_period_id is not None:
            period = self._organizations.get_reporting_period(run.reporting_period_id)
            if isinstance(period, ReportingPeriod):
                period_label = period.label
        source_file_name: str | None = None
        if run.source_file_id is not None:
            file = self._financials.get_file(run.source_file_id)
            if isinstance(file, FinancialFile):
                source_file_name = file.file_name
        return OrganizationContext(
            organization_id=organization_id,
            organization_name=org_name,
            period_label=period_label,
            source_file_name=source_file_name,
        )

    def _load_baseline(
        self,
        organization_id: uuid.UUID,
        provenance: dict[str, Any],
    ) -> BaselineWasteContext | None:
        baseline_id_raw = provenance.get("baseline_analysis_run_id")
        if baseline_id_raw is None:
            return None
        try:
            baseline_run_id = uuid.UUID(str(baseline_id_raw))
        except ValueError:
            return None
        baseline_run = self._analyses.get(baseline_run_id)
        if (
            baseline_run is None
            or baseline_run.organization_id != organization_id
            or baseline_run.analysis_type != AnalysisType.FINANCIAL_WASTE
            or baseline_run.status != AnalysisRunStatus.COMPLETED
        ):
            return None
        waste_result = self._waste.get_result_for_run(baseline_run.id)
        if waste_result is None:
            return None
        metadata = dict(baseline_run.runtime_metadata or {})
        ai_insights = metadata.get("ai_insights")
        if ai_insights is not None and not isinstance(ai_insights, dict):
            ai_insights = None
        return BaselineWasteContext(
            waste_result=waste_result,
            category_breakdowns=tuple(
                self._waste.list_category_breakdowns(baseline_run.id)
            ),
            ai_insights=ai_insights,
        )


def compute_input_fingerprint(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def waste_input_fingerprint(inputs: WasteReportInputs) -> str:
    return compute_input_fingerprint(
        {
            "run_id": str(inputs.run.id),
            "facts": inputs.facts.to_dict(),
            "waste_result_id": str(inputs.waste_result.id),
            "breakdown_ids": [str(b.id) for b in inputs.category_breakdowns],
            "vendor_ids": [str(v.id) for v in inputs.vendor_findings],
            "recommendation_ids": [str(r.id) for r in inputs.recommendations],
            "ai_insights": inputs.ai_insights,
        }
    )


def scenario_input_fingerprint(inputs: ScenarioReportInputs) -> str:
    baseline_key: dict[str, Any] | None = None
    if inputs.baseline is not None:
        baseline_key = {
            "waste_result_id": str(inputs.baseline.waste_result.id),
            "breakdown_ids": [
                str(b.id) for b in inputs.baseline.category_breakdowns
            ],
        }
    return compute_input_fingerprint(
        {
            "run_id": str(inputs.run.id),
            "facts": inputs.facts.to_dict(),
            "simulation_run_id": str(inputs.simulation_run.id),
            "scenario_id": str(inputs.scenario.id),
            "forecast_id": str(inputs.forecast_summary.id),
            "chart_point_ids": [str(p.id) for p in inputs.chart_points],
            "comparison_metric_ids": [str(m.id) for m in inputs.comparison_metrics],
            "impact_item_ids": [str(i.id) for i in inputs.impact_items],
            "action_item_ids": [str(a.id) for a in inputs.action_items],
            "scenario_provenance": inputs.scenario_provenance,
            "baseline": baseline_key,
        }
    )
