"""Risk Fact Assembler unit tests."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.business.assemblers.risk import RiskFactAssembler
from app.business.engines.risk.calculator import RiskCalculationResult
from app.business.engines.risk.detector import RiskDetectionResult
from app.business.engines.risk.engine import RiskEngine
from tests.business.risk_conftest import sample_risk_input


def test_risk_fact_assembler_produces_required_facts() -> None:
    engine = RiskEngine()
    output = engine.run(sample_risk_input())
    contract = RiskFactAssembler().assemble(output.calculation, output.detection)

    metrics = {fact.metric for fact in contract.facts}
    assert "risk.total_findings" in metrics
    assert "risk.high_priority_count" in metrics
    assert "risk.overall_posture_level" in metrics
    assert "risk.liquidity_ratio" in metrics
    assert contract.engine_id == "risk"
    assert contract.generated_at == datetime(2026, 7, 16, tzinfo=UTC)


def test_risk_fact_assembler_empty_findings() -> None:
    calc = RiskCalculationResult(
        total_spend=Decimal("1000"),
        total_waste_amount=Decimal("10"),
        waste_percentage=Decimal("1.00"),
        budget_total=None,
        actual_total=None,
        budget_variance_percentage=None,
        liquidity_ratio=Decimal("100.00"),
        top_category_name=None,
        top_category_concentration=None,
        category_count=1,
        organization_id="org",
        snapshot_id="snap",
        reporting_period="2026-Q2",
        source_dataset="test",
        generated_at=datetime(2026, 7, 16, tzinfo=UTC),
    )
    detection = RiskDetectionResult(
        findings=(),
        overall_posture_level="low",
        high_count=0,
        medium_count=0,
        low_count=0,
    )
    contract = RiskFactAssembler().assemble(calc, detection)
    total = next(f for f in contract.facts if f.metric == "risk.total_findings")
    assert total.value == "0"
