"""Scenario Fact Assembler — maps calculator output to Facts Contract."""

from __future__ import annotations

from datetime import UTC, datetime

from app.business.engines.scenario.calculator import ScenarioCalculationResult
from app.business.engines.scenario.detector import ScenarioDetectionResult
from app.business.engines.scenario.manifest import (
    ENGINE_ID,
    ENGINE_VERSION,
    FACTS_CONTRACT_VERSION,
)
from app.business.facts.contract import Fact, FactsContract


class ScenarioFactAssembler:
    """Deterministic mapping only — no calculations or interpretation."""

    def assemble(
        self,
        calculation: ScenarioCalculationResult,
        detection: ScenarioDetectionResult,
    ) -> FactsContract:
        timestamp = calculation.generated_at or datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
        source = f"{ENGINE_ID}:{calculation.source_dataset}"
        org_id = calculation.organization_id
        period = calculation.period
        facts: list[Fact] = [
            Fact(
                domain="scenario",
                metric="scenario.archetype",
                value=calculation.archetype.value,
                source=source,
                organization_id=org_id,
                period=period,
            ),
            Fact(
                domain="scenario",
                metric="scenario.baseline_total",
                value=str(calculation.baseline_total),
                unit="currency",
                source=source,
                organization_id=org_id,
                period=period,
            ),
            Fact(
                domain="scenario",
                metric="scenario.projected_total",
                value=str(calculation.projected_total),
                unit="currency",
                source=source,
                organization_id=org_id,
                period=period,
            ),
            Fact(
                domain="scenario",
                metric="scenario.delta_amount",
                value=str(calculation.delta_amount),
                unit="currency",
                source=source,
                organization_id=org_id,
                period=period,
            ),
            Fact(
                domain="scenario",
                metric="scenario.delta_percent",
                value=str(calculation.delta_percent),
                unit="percent",
                severity=detection.overall_direction,
                source=source,
                organization_id=org_id,
                period=period,
            ),
            Fact(
                domain="scenario",
                metric="scenario.horizon_quarters",
                value=str(calculation.horizon_quarters),
                source=source,
                organization_id=org_id,
                period=period,
            ),
            Fact(
                domain="scenario",
                metric="scenario.confidence_percent",
                value=str(calculation.confidence_percent),
                unit="percent",
                source=source,
                organization_id=org_id,
                period=period,
            ),
        ]
        for category in calculation.categories:
            facts.append(
                Fact(
                    domain="scenario",
                    metric="scenario.category_baseline",
                    value=str(category.baseline_amount),
                    unit="currency",
                    source=source,
                    organization_id=org_id,
                    period=period,
                    metadata={"category_name": category.category_name},
                )
            )
            facts.append(
                Fact(
                    domain="scenario",
                    metric="scenario.category_projected",
                    value=str(category.projected_amount),
                    unit="currency",
                    source=source,
                    organization_id=org_id,
                    period=period,
                    metadata={"category_name": category.category_name},
                )
            )
        return FactsContract(
            contract_version=FACTS_CONTRACT_VERSION,
            engine_id=ENGINE_ID,
            engine_version=ENGINE_VERSION,
            generated_at=timestamp,
            facts=tuple(facts),
        )
