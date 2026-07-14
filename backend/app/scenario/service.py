"""Scenario Analysis orchestration — Snapshot + Parameters → Engine → Gold (Sprint 6.5)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.business.engines.scenario.calculator import ScenarioCalculator
from app.business.engines.scenario.manifest import ENGINE_ID
from app.business.exceptions import EngineError
from app.business.facts.contract import FactsContract
from app.business.registry import get_engine
from app.db.models import (
    AnalysisRun,
    FinancialSnapshot,
    SimulationActionItem,
    SimulationChartPoint,
    SimulationComparisonMetric,
    SimulationForecastSummary,
    SimulationImpactItem,
    SimulationRun,
)
from app.db.models.enums import (
    AnalysisRunStatus,
    AnalysisType,
    ProcessingStatus,
    SimulationScenarioStatus,
)
from app.decision.exceptions import SnapshotAdapterError
from app.repositories import (
    AnalysisRepository,
    FinancialRepository,
    FinancialSnapshotRepository,
    OrganizationRepository,
    SimulationRepository,
    WasteRepository,
)
from app.scenario.adapters.assumptions import ScenarioAssumptionsAdapter
from app.scenario.adapters.snapshot_v1 import ScenarioSnapshotAdapterV1
from app.scenario.baseline import validate_waste_baseline_alignment
from app.scenario.mappers.scenario_gold import ScenarioGoldMapper
from app.services.analysis import AnalysisService
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    InvalidStateError,
    ResourceNotFoundError,
)
from app.services.simulation import SimulationService


@dataclass(frozen=True, slots=True)
class ScenarioExecutionOutcome:
    """Result of a successful scenario execution."""

    analysis_run: AnalysisRun
    simulation_run: SimulationRun
    facts_contract: FactsContract
    snapshot: FinancialSnapshot


class ScenarioService(BaseService):
    """Deterministic scenario path without AI."""

    def __init__(
        self,
        session: Session,
        analysis_service: AnalysisService,
        analysis_repository: AnalysisRepository,
        simulation_repository: SimulationRepository,
        snapshot_repository: FinancialSnapshotRepository,
        financial_repository: FinancialRepository,
        organization_repository: OrganizationRepository,
        waste_repository: WasteRepository,
        *,
        snapshot_adapter: ScenarioSnapshotAdapterV1 | None = None,
        assumptions_adapter: ScenarioAssumptionsAdapter | None = None,
    ) -> None:
        super().__init__(session)
        self._analysis = analysis_service
        self._analyses = analysis_repository
        self._simulations = simulation_repository
        self._snapshots = snapshot_repository
        self._financials = financial_repository
        self._organizations = organization_repository
        self._waste = waste_repository
        self._snapshot_adapter = snapshot_adapter or ScenarioSnapshotAdapterV1()
        self._assumptions_adapter = assumptions_adapter or ScenarioAssumptionsAdapter()
        self._calculator = ScenarioCalculator()

    def execute_scenario(
        self,
        organization_id: uuid.UUID,
        scenario_id: uuid.UUID,
        *,
        source_file_id: uuid.UUID,
        source_snapshot_id: uuid.UUID | None = None,
        snapshot_version: int | None = None,
        baseline_analysis_run_id: uuid.UUID | None = None,
        reporting_period_id: uuid.UUID | None = None,
    ) -> ScenarioExecutionOutcome:
        if snapshot_version is not None and source_snapshot_id is not None:
            raise BusinessValidationError(
                "Provide either source_snapshot_id or snapshot_version, not both"
            )

        scenario = self._simulations.get_scenario(scenario_id)
        if scenario is None:
            raise ResourceNotFoundError("SimulationScenario", scenario_id)
        self._check_ownership(scenario, "SimulationScenario", organization_id)

        source_file = self._financials.get_file(source_file_id)
        if source_file is None:
            raise ResourceNotFoundError("FinancialFile", source_file_id)
        self._check_ownership(source_file, "FinancialFile", organization_id)
        if source_file.processing_status != ProcessingStatus.READY_FOR_ANALYSIS:
            raise InvalidStateError(
                "Source file must be ready for analysis before scenario execution "
                f"(current status: '{source_file.processing_status}')"
            )

        snapshot = self._resolve_snapshot(
            organization_id,
            source_file_id,
            source_snapshot_id=source_snapshot_id,
            snapshot_version=snapshot_version,
        )
        period_label = self._resolve_period_label(snapshot, reporting_period_id)
        assumptions = self._simulations.list_assumptions(scenario_id)

        run = self._analysis.create_run(
            organization_id,
            analysis_type=AnalysisType.SIMULATION,
            title=scenario.name,
            source_file_id=source_file_id,
            source_snapshot_id=snapshot.id,
            reporting_period_id=reporting_period_id or snapshot.reporting_period_id,
            runtime_metadata={
                "scenario_engine": "scenario_v1",
                "scenario_id": str(scenario_id),
                "snapshot_version": snapshot.snapshot_version,
            },
        )
        self._analysis.start_run(organization_id, run.id)
        simulation_run = self._simulations.create_run(
            SimulationRun(scenario_id=scenario.id, analysis_run_id=run.id)
        )

        try:
            baseline = self._snapshot_adapter.adapt(
                snapshot.payload,
                organization_id=str(organization_id),
                period=period_label,
            )
            if baseline_analysis_run_id is not None:
                self._cross_check_baseline(
                    organization_id, baseline_analysis_run_id, baseline.total_baseline
                )
            engine_input = self._assumptions_adapter.adapt(
                assumptions,
                scenario_name=scenario.name,
                scenario_description=scenario.description,
                baseline=baseline,
            )
            engine = get_engine(ENGINE_ID)
            facts = engine.run(engine_input)
            calculation = self._calculator.calculate(engine_input)
            gold_payload = ScenarioGoldMapper.to_record_payload(calculation, facts)
            provenance = {
                "scenario_id": str(scenario_id),
                "archetype": engine_input.archetype.value,
                "engine_id": facts.engine_id,
                "engine_version": facts.engine_version,
                "source_snapshot_id": str(snapshot.id),
                "snapshot_version": snapshot.snapshot_version,
            }
            if baseline_analysis_run_id is not None:
                provenance["baseline_analysis_run_id"] = str(baseline_analysis_run_id)

            with self._transaction():
                self._persist_gold(simulation_run.id, gold_payload)
            completed = self._analysis.complete_run(
                organization_id,
                run.id,
                success_metadata={
                    "facts_contract": facts.to_dict(),
                    "scenario_provenance": provenance,
                },
            )
            if scenario.status != SimulationScenarioStatus.COMPLETED:
                with self._transaction():
                    self._simulations.update_scenario(
                        scenario, {"status": SimulationScenarioStatus.COMPLETED}
                    )
        except SnapshotAdapterError as exc:
            self._analysis.fail_run(
                organization_id,
                run.id,
                failure_details=exc.to_failure_details(),
            )
            raise
        except EngineError as exc:
            self._analysis.fail_run(
                organization_id,
                run.id,
                failure_details={
                    "error_code": "engine_execution_failed",
                    "message": str(exc),
                },
            )
            raise

        updated_run = self._simulations.get_run(simulation_run.id) or simulation_run
        return ScenarioExecutionOutcome(
            analysis_run=completed,
            facts_contract=facts,
            simulation_run=updated_run,
            snapshot=snapshot,
        )

    def _cross_check_baseline(
        self,
        organization_id: uuid.UUID,
        baseline_analysis_run_id: uuid.UUID,
        snapshot_baseline_total: float,
    ) -> None:
        run = self._analyses.get(baseline_analysis_run_id)
        if run is None:
            raise ResourceNotFoundError("AnalysisRun", baseline_analysis_run_id)
        self._check_ownership(run, "AnalysisRun", organization_id)
        if run.analysis_type != AnalysisType.FINANCIAL_WASTE:
            raise InvalidStateError(
                "Baseline analysis run must be a completed financial_waste run"
            )
        if run.status != AnalysisRunStatus.COMPLETED:
            raise InvalidStateError("Baseline analysis run must be completed")
        waste_result = self._waste.get_result_for_run(run.id)
        if waste_result is None:
            raise InvalidStateError(
                "Baseline analysis run has no waste_analysis_results record"
            )
        metadata = run.runtime_metadata or {}
        facts_payload = metadata.get("facts_contract")
        if not isinstance(facts_payload, dict):
            raise InvalidStateError(
                "Baseline analysis run is missing facts_contract metadata"
            )
        facts = FactsContract.from_dict(facts_payload)
        validate_waste_baseline_alignment(
            snapshot_baseline_total=snapshot_baseline_total,
            facts_contract=facts,
        )

    def _persist_gold(
        self, simulation_run_id: uuid.UUID, payload: dict[str, Any]
    ) -> None:
        self._simulations.update_run(
            self._simulations.require_run(simulation_run_id),
            {
                "result_title": payload.get("result_title"),
                "result_description": payload.get("result_description"),
                "confidence_label": payload.get("confidence_label"),
            },
        )
        summary = SimulationService._build_forecast_summary(
            simulation_run_id, payload["forecast_summary"]
        )
        self._simulations.set_forecast_summary(summary)
        chart_rows = [
            SimulationChartPoint(simulation_run_id=simulation_run_id, **point)
            for point in payload["chart_points"]
        ]
        if chart_rows:
            self._simulations.add_chart_points(chart_rows)
        metric_rows = [
            SimulationComparisonMetric(simulation_run_id=simulation_run_id, **metric)
            for metric in payload["comparison_metrics"]
        ]
        if metric_rows:
            self._simulations.add_comparison_metrics(metric_rows)
        impact_rows = [
            SimulationImpactItem(simulation_run_id=simulation_run_id, **item)
            for item in payload["impact_items"]
        ]
        if impact_rows:
            self._simulations.add_impact_items(impact_rows)
        action_rows = [
            SimulationActionItem(simulation_run_id=simulation_run_id, **item)
            for item in payload["action_items"]
        ]
        if action_rows:
            self._simulations.add_action_items(action_rows)

    def _resolve_snapshot(
        self,
        organization_id: uuid.UUID,
        source_file_id: uuid.UUID,
        *,
        source_snapshot_id: uuid.UUID | None,
        snapshot_version: int | None,
    ) -> FinancialSnapshot:
        if source_snapshot_id is not None:
            snapshot = self._snapshots.get_snapshot(source_snapshot_id)
            if snapshot is None:
                raise ResourceNotFoundError("FinancialSnapshot", source_snapshot_id)
        elif snapshot_version is not None:
            snapshot = self._snapshots.get_snapshot_by_file_version(
                source_file_id, snapshot_version
            )
            if snapshot is None:
                raise ResourceNotFoundError(
                    "FinancialSnapshot",
                    f"{source_file_id}:v{snapshot_version}",
                )
        else:
            snapshot = self._snapshots.get_latest_snapshot_for_file(source_file_id)
            if snapshot is None:
                raise ResourceNotFoundError(
                    "FinancialSnapshot",
                    f"latest for file {source_file_id}",
                )

        self._check_ownership(snapshot, "FinancialSnapshot", organization_id)
        if snapshot.financial_file_id != source_file_id:
            raise BusinessValidationError(
                "Snapshot does not belong to the requested source file"
            )
        return snapshot

    def _resolve_period_label(
        self,
        snapshot: FinancialSnapshot,
        reporting_period_id: uuid.UUID | None,
    ) -> str | None:
        period_id = reporting_period_id or snapshot.reporting_period_id
        if period_id is None:
            return None
        period = self._organizations.get_reporting_period(period_id)
        if period is None:
            return None
        return period.label
