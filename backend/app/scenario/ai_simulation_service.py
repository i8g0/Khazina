"""AI-native simulation orchestration (Sprint 5)."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.business.engines.scenario.universal_calculator import (
    UniversalScenarioCalculator,
    UniversalScenarioInput,
)
from app.business.facts.contract import CONTRACT_VERSION, Fact, FactsContract
from app.core.logging import get_logger
from app.db.models import AnalysisRun, FinancialSnapshot, SimulationRun
from app.db.models.enums import AnalysisType, ProcessingStatus, SimulationScenarioStatus
from app.observability.persistence import load_file_timeline, merge_run_timeline
from app.observability.pipeline import PipelineStage, PipelineTimeline, load_pipeline_timeline
from app.observability.structured_log import log_pipeline_event
from app.repositories import (
    AnalysisRepository,
    FinancialRepository,
    FinancialSnapshotRepository,
    OrganizationRepository,
    SimulationRepository,
    WasteRepository,
)
from app.scenario.adapters.snapshot_v1 import ScenarioSnapshotAdapterV1
from app.scenario.ai_contract import InterpretedScenario, SimulationExplanation
from app.scenario.ai_explainer import AISimulationExplainer
from app.scenario.ai_interpreter import AIScenarioInterpreter
from app.scenario.mappers.ai_gold_mapper import AISimulationGoldMapper
from app.scenario.service import ScenarioService
from app.services.analysis import AnalysisService
from app.services.base import BaseService
from app.services.exceptions import InvalidStateError, ResourceNotFoundError
from app.services.simulation import SimulationService

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class AISimulationOutcome:
    analysis_run: AnalysisRun
    simulation_run: SimulationRun
    snapshot: FinancialSnapshot
    user_request: str
    interpreted_scenario: InterpretedScenario
    explanation: SimulationExplanation


class AISimulationService(BaseService):
    """Natural language → AI interpret → engine → AI explain → Gold."""

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
        interpreter: AIScenarioInterpreter | None = None,
        calculator: UniversalScenarioCalculator | None = None,
        explainer: AISimulationExplainer | None = None,
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
        self._interpreter = interpreter or AIScenarioInterpreter()
        self._calculator = calculator or UniversalScenarioCalculator()
        self._explainer = explainer or AISimulationExplainer()
        self._simulation = SimulationService(
            session,
            simulation_repository,
            analysis_repository,
            organization_repository,
        )
        self._scenario_helper = ScenarioService(
            session,
            analysis_service,
            analysis_repository,
            simulation_repository,
            snapshot_repository,
            financial_repository,
            organization_repository,
            waste_repository,
            snapshot_adapter=self._snapshot_adapter,
        )

    def execute(
        self,
        organization_id: uuid.UUID,
        *,
        user_request: str,
        source_file_id: uuid.UUID,
        source_snapshot_id: uuid.UUID | None = None,
        snapshot_version: int | None = None,
        baseline_analysis_run_id: uuid.UUID | None = None,
        reporting_period_id: uuid.UUID | None = None,
        initiating_user_id: uuid.UUID | None = None,
    ) -> AISimulationOutcome:
        cleaned = user_request.strip()
        if not cleaned:
            raise InvalidStateError("user_request must not be empty")

        source_file = self._financials.get_file(source_file_id)
        if source_file is None:
            raise ResourceNotFoundError("FinancialFile", source_file_id)
        self._check_ownership(source_file, "FinancialFile", organization_id)
        if source_file.processing_status != ProcessingStatus.READY_FOR_ANALYSIS:
            raise InvalidStateError(
                f"Source file must be ready for analysis (status={source_file.processing_status})"
            )

        snapshot = self._scenario_helper._resolve_snapshot(
            organization_id,
            source_file_id,
            source_snapshot_id=source_snapshot_id,
            snapshot_version=snapshot_version,
        )
        period_label = self._scenario_helper._resolve_period_label(snapshot, reporting_period_id)
        baseline = self._snapshot_adapter.adapt(
            snapshot.payload,
            organization_id=str(organization_id),
            period=period_label,
        )
        if baseline_analysis_run_id is not None:
            self._scenario_helper._cross_check_baseline(
                organization_id, baseline_analysis_run_id, baseline.total_baseline
            )

        interpreted = self._interpreter.interpret(cleaned, baseline=baseline)
        calculation = self._calculator.calculate(
            UniversalScenarioInput(
                interpreted=interpreted,
                baseline=baseline,
                user_request=cleaned,
            )
        )
        explanation = self._explainer.explain(
            user_request=cleaned,
            interpreted=interpreted,
            calculation=calculation,
        )

        scenario = self._simulation.create_scenario(
            organization_id,
            name=interpreted.title_ar[:200],
            description=cleaned,
        )
        self._persist_assumptions_from_interpretation(scenario.id, interpreted)

        run = self._analysis.create_run(
            organization_id,
            analysis_type=AnalysisType.SIMULATION,
            title=interpreted.title_ar[:500],
            source_file_id=source_file_id,
            source_snapshot_id=snapshot.id,
            reporting_period_id=reporting_period_id or snapshot.reporting_period_id,
            runtime_metadata={
                "simulation_engine": "ai_native_v1",
                "user_request": cleaned,
                "interpreted_scenario": interpreted.to_dict(),
                "ai_explanation": explanation.to_dict(),
            },
        )
        self._analysis.start_run(organization_id, run.id)
        simulation_run = self._simulations.create_run(
            SimulationRun(scenario_id=scenario.id, analysis_run_id=run.id)
        )

        facts = FactsContract(
            contract_version=CONTRACT_VERSION,
            engine_id="scenario_ai_v1",
            engine_version="1.0.0",
            generated_at=calculation.generated_at,
            facts=(
                Fact(
                    domain="simulation",
                    metric="scenario_type",
                    value=interpreted.scenario_type,
                    source="scenario_ai_v1",
                ),
                Fact(
                    domain="simulation",
                    metric="delta_percent",
                    value=f"{calculation.delta_percent:.2f}",
                    source="scenario_ai_v1",
                    unit="percent",
                ),
            ),
        )
        gold_payload = AISimulationGoldMapper.to_record_payload(
            calculation,
            interpreted=interpreted,
            explanation=explanation,
            user_request=cleaned,
        )

        timeline = PipelineTimeline(
            organization_id=str(organization_id),
            file_id=str(source_file_id),
            snapshot_id=str(snapshot.id),
            analysis_run_id=str(run.id),
            inherited=load_file_timeline(source_file),
        )
        started = time.perf_counter()
        timeline.start_stage(PipelineStage.SIMULATION_STARTED)

        with self._transaction():
            self._scenario_helper._persist_gold(simulation_run.id, gold_payload)
            self._simulations.update_scenario(
                scenario,
                {"status": SimulationScenarioStatus.COMPLETED, "description": cleaned},
            )

        timeline.complete_stage(PipelineStage.SIMULATION_COMPLETED)
        completed = self._analysis.complete_run(
            organization_id,
            run.id,
            success_metadata={
                "facts_contract": facts.to_dict(),
                "scenario_provenance": {
                    "scenario_id": str(scenario.id),
                    "engine_id": "scenario_ai_v1",
                    "scenario_type": interpreted.scenario_type,
                    "source_snapshot_id": str(snapshot.id),
                    "baseline_analysis_run_id": (
                        str(baseline_analysis_run_id) if baseline_analysis_run_id else None
                    ),
                },
                "user_request": cleaned,
                "interpreted_scenario": interpreted.to_dict(),
                "ai_explanation": explanation.to_dict(),
                "pipeline_timeline": timeline.to_list(),
            },
            initiating_user_id=initiating_user_id,
        )

        if baseline_analysis_run_id is not None:
            self._scenario_helper._append_simulation_to_baseline(
                organization_id, baseline_analysis_run_id, timeline
            )

        log_pipeline_event(
            logger,
            "ai_simulation_completed",
            organization_id=str(organization_id),
            analysis_run_id=str(run.id),
            scenario_type=interpreted.scenario_type,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )

        updated_run = self._simulations.get_run(simulation_run.id) or simulation_run
        return AISimulationOutcome(
            analysis_run=completed,
            simulation_run=updated_run,
            snapshot=snapshot,
            user_request=cleaned,
            interpreted_scenario=interpreted,
            explanation=explanation,
        )

    def _persist_assumptions_from_interpretation(
        self, scenario_id: uuid.UUID, interpreted: InterpretedScenario
    ) -> None:
        from app.db.models import SimulationAssumption

        order = 0
        for action in interpreted.actions:
            label = action.description or action.action_type
            value_parts: list[str] = []
            if action.mode == "percent" and action.value is not None:
                value_parts.append(f"{action.value}%")
            if action.amount is not None:
                value_parts.append(f"{action.amount:,.0f} SAR")
            if action.category:
                value_parts.append(action.category)
            self._simulations.add_assumptions(
                [
                    SimulationAssumption(
                        scenario_id=scenario_id,
                        label=label[:200],
                        value=" | ".join(value_parts) or action.action_type,
                        display_order=order,
                    )
                ]
            )
            order += 1
        for assumption in interpreted.assumptions:
            self._simulations.add_assumptions(
                [
                    SimulationAssumption(
                        scenario_id=scenario_id,
                        label="افتراض",
                        value=assumption[:500],
                        display_order=order,
                    )
                ]
            )
            order += 1
