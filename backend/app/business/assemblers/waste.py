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
from app.presentation.waste_category_labels import waste_category_label_ar


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

        if period:
            facts.append(
                Fact(
                    domain="waste",
                    metric="waste.reporting_period",
                    value=period,
                    source=source,
                    organization_id=org_id,
                    period=period,
                    confidence="deterministic",
                )
            )

        facts.append(
            Fact(
                domain="waste",
                metric="waste.currency",
                value="SAR",
                source=source,
                organization_id=org_id,
                period=period,
                confidence="deterministic",
            )
        )
        facts.append(
            Fact(
                domain="waste",
                metric="waste.evidence_source",
                value=calculation.source_dataset,
                source=source,
                organization_id=org_id,
                period=period,
                confidence="deterministic",
            )
        )

        facts.append(
            Fact(
                domain="waste",
                metric="waste.total_amount",
                value=str(calculation.total_waste_amount),
                unit="currency",
                source=source,
                organization_id=org_id,
                period=period,
                confidence="deterministic",
            )
        )
        facts.append(
            Fact(
                domain="waste",
                metric="waste.financial_impact",
                value=str(calculation.total_waste_amount),
                unit="currency",
                source=source,
                organization_id=org_id,
                period=period,
                confidence="deterministic",
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
                confidence="deterministic",
            )
        )
        if calculation.top_category_name is not None:
            top_label = waste_category_label_ar(calculation.top_category_name)
            facts.append(
                Fact(
                    domain="waste",
                    metric="waste.top_category",
                    value=calculation.top_category_name,
                    source=source,
                    organization_id=org_id,
                    period=period,
                    metadata={
                        "category_name": calculation.top_category_name,
                        "category_label_ar": top_label,
                    },
                    confidence="deterministic",
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
                    confidence="deterministic",
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
                confidence="deterministic",
            )
        )
        facts.append(
            Fact(
                domain="waste",
                metric="waste.savings_opportunity",
                value=str(calculation.potential_savings_amount),
                unit="currency",
                source=source,
                organization_id=org_id,
                period=period,
                confidence="deterministic",
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
                confidence="deterministic",
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
                confidence="deterministic",
            )
        )
        facts.append(
            Fact(
                domain="waste",
                metric="waste.category_count",
                value=str(len(calculation.categories)),
                unit="count",
                source=source,
                organization_id=org_id,
                period=period,
                confidence="deterministic",
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
            category_label = waste_category_label_ar(category.category_name)
            category_meta = {
                "category_name": category.category_name,
                "category_label_ar": category_label,
            }
            facts.append(
                Fact(
                    domain="waste",
                    metric="waste.category_amount",
                    value=str(category.amount),
                    unit="currency",
                    source=source,
                    organization_id=org_id,
                    period=period,
                    metadata=category_meta,
                    confidence="deterministic",
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
                    metadata=category_meta,
                    confidence="deterministic",
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
                        metadata=category_meta,
                        confidence="deterministic",
                    )
                )

        executive_context: dict[str, str | int] = {}
        if period:
            executive_context["reporting_period_label"] = period
        if org_id:
            executive_context["organization_id"] = org_id
        executive_context["category_count"] = len(calculation.categories)
        if calculation.top_category_name:
            executive_context["top_driver"] = waste_category_label_ar(
                calculation.top_category_name
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
                "executive_context": executive_context,
            },
        )
