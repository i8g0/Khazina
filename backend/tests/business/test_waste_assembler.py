"""Waste Fact Assembler unit tests."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.business.assemblers.waste import WasteFactAssembler
from app.business.engines.waste.calculator import (
    WasteCalculationResult,
    WasteCategoryCalculation,
)
from app.business.engines.waste.detector import (
    WasteCategoryDetection,
    WasteDetectionEvent,
    WasteDetectionResult,
    WasteLevel,
)
from app.business.engines.waste.manifest import SUPPORTED_FACTS


def test_waste_fact_assembler_produces_expected_facts() -> None:
    calculation = WasteCalculationResult(
        total_spend=Decimal("50000000.00"),
        total_waste_amount=Decimal("2340000.00"),
        waste_percentage=Decimal("4.68"),
        categories=(
            WasteCategoryCalculation("finance", Decimal("1075000.00"), Decimal("45.94")),
        ),
        top_category_name="finance",
        top_category_percentage=Decimal("45.94"),
        recoverable_savings_rate=Decimal("0.80"),
        potential_savings_amount=Decimal("1872000.00"),
        active_savings_opportunities=1,
        organization_id="org-123",
        period="2026-Q2",
        source_dataset="waste_analysis",
        generated_at=datetime(2026, 7, 13, tzinfo=UTC),
    )
    detection = WasteDetectionResult(
        overall_waste_level=WasteLevel.LOW,
        category_detections=(
            WasteCategoryDetection("finance", WasteLevel.HIGH),
        ),
        events=(
            WasteDetectionEvent(
                event_type="waste_level_classification",
                classification=WasteLevel.LOW,
                metric="waste.percentage",
                value="4.68",
                threshold_applied="overall_waste_percentage<5.00",
            ),
        ),
    )

    contract = WasteFactAssembler().assemble(calculation, detection)
    metrics = {fact.metric for fact in contract.facts}

    assert contract.engine_id == "waste"
    assert contract.contract_version == "1.0"
    assert metrics.issuperset(set(SUPPORTED_FACTS))
    assert all(fact.value for fact in contract.facts)
    assert all(
        not any(key in fact.to_dict() for key in ("narrative", "summary", "text"))
        for fact in contract.facts
    )
