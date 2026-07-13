"""Waste Fact Assembler — maps calculator and detector outputs to Facts Contract."""

from __future__ import annotations

from datetime import UTC, datetime

from app.business.engines.waste.calculator import WasteCalculationResult
from app.business.engines.waste.detector import WasteDetectionResult
from app.business.engines.waste.manifest import (
    ENGINE_ID,
    ENGINE_VERSION,
    FACTS_CONTRACT_VERSION,
    WASTE_ENGINE_MANIFEST,
)
from app.business.facts.contract import Fact, FactsContract


class WasteFactAssembler:
    """Deterministic mapping only — no calculations or interpretation."""

    def assemble(
        self,
        calculation: WasteCalculationResult,
        detection: WasteDetectionResult,
    ) -> FactsContract:
        timestamp = calculation.generated_at or datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        source = f"{ENGINE_ID}:{calculation.source_dataset}"
        org_id = calculation.organization_id
        period = calculation.period
        facts: list[Fact] = []

        facts.append(
            Fact(
                domain="waste",
                metric="waste.total_amount",
                value=str(calculation.total_waste_amount),
                unit="currency",
                source=source,
                organization_id=org_id,
                period=period,
            )
        )
        facts.append(
            Fact(
                domain="waste",
                metric="waste.percentage",
                value=str(calculation.waste_percentage),
                unit="percent",
                severity=detection.overall_waste_level.value,
                source=source,
                organization_id=org_id,
                period=period,
            )
        )
        if calculation.top_category_name is not None:
            facts.append(
                Fact(
                    domain="waste",
                    metric="waste.top_category",
                    value=calculation.top_category_name,
                    source=source,
                    organization_id=org_id,
                    period=period,
                )
            )
        if calculation.top_category_percentage is not None:
            facts.append(
                Fact(
                    domain="waste",
                    metric="waste.top_category_percentage",
                    value=str(calculation.top_category_percentage),
                    unit="percent",
                    source=source,
                    organization_id=org_id,
                    period=period,
                )
            )
        facts.append(
            Fact(
                domain="waste",
                metric="waste.potential_savings",
                value=str(calculation.potential_savings_amount),
                unit="currency",
                source=source,
                organization_id=org_id,
                period=period,
            )
        )
        facts.append(
            Fact(
                domain="waste",
                metric="waste.savings_opportunities",
                value=str(calculation.active_savings_opportunities),
                unit="count",
                source=source,
                organization_id=org_id,
                period=period,
            )
        )
        facts.append(
            Fact(
                domain="waste",
                metric="waste.overall_level",
                value=detection.overall_waste_level.value,
                severity=detection.overall_waste_level.value,
                source=source,
                organization_id=org_id,
                period=period,
            )
        )

        for category in calculation.categories:
            category_level = next(
                (
                    item.waste_level.value
                    for item in detection.category_detections
                    if item.category_name == category.category_name
                ),
                None,
            )
            facts.append(
                Fact(
                    domain="waste",
                    metric="waste.category_amount",
                    value=str(category.amount),
                    unit="currency",
                    source=source,
                    organization_id=org_id,
                    period=period,
                    metadata={"category_name": category.category_name},
                )
            )
            facts.append(
                Fact(
                    domain="waste",
                    metric="waste.category_percentage",
                    value=str(category.percentage_of_waste),
                    unit="percent",
                    severity=category_level,
                    source=source,
                    organization_id=org_id,
                    period=period,
                    metadata={"category_name": category.category_name},
                )
            )
            if category_level is not None:
                facts.append(
                    Fact(
                        domain="waste",
                        metric="waste.category_level",
                        value=category_level,
                        severity=category_level,
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
            extensions={
                "engine_name": WASTE_ENGINE_MANIFEST.engine_name,
                "supported_facts": list(WASTE_ENGINE_MANIFEST.supported_facts),
            },
        )
