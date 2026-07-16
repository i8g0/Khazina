"""Risk Engine lifecycle unit tests."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.business.engines.risk.engine import RiskEngine
from app.business.engines.risk.input import FinancialMetricsInput, RiskEngineInput
from app.business.engines.risk.manifest import RISK_ENGINE_MANIFEST
from app.business.exceptions import (
    BusinessRuleViolationError,
    InvalidInputError,
    MissingDataError,
    ValidationError,
)
from tests.business.risk_conftest import sample_risk_input


def test_risk_engine_lifecycle_returns_output_with_facts_and_findings() -> None:
    engine = RiskEngine()
    output = engine.run(sample_risk_input())

    assert output.facts_contract.engine_id == "risk"
    assert output.facts_contract.engine_version == "1.0.0"
    assert len(output.findings) >= 1
    assert all(f.finding_status == "detected" for f in output.findings)
    assert output.overall_posture_level in {"elevated", "moderate", "low"}

    total_fact = next(
        f for f in output.facts_contract.facts if f.metric == "risk.total_findings"
    )
    assert total_fact.value == str(len(output.findings))


def test_risk_engine_manifest_complete() -> None:
    manifest = RiskEngine().manifest
    assert manifest.engine_id == "risk"
    assert manifest.engine_version == "1.0.0"
    assert manifest.supported_facts == RISK_ENGINE_MANIFEST.supported_facts


def test_risk_engine_findings_are_deterministic() -> None:
    engine = RiskEngine()
    first = engine.run(sample_risk_input())
    second = engine.run(sample_risk_input())
    assert [f.finding_id for f in first.findings] == [f.finding_id for f in second.findings]
    assert [f.score for f in first.findings] == [f.score for f in second.findings]


def test_risk_engine_no_register_promotion() -> None:
    """Findings remain analytical outputs with detected status only."""
    output = RiskEngine().run(sample_risk_input())
    for finding in output.findings:
        assert finding.finding_status == "detected"
        assert "promoted" not in finding.evidence


@pytest.mark.parametrize(
    ("input_data", "expected"),
    [
        (
            RiskEngineInput(
                organization_id="",
                snapshot_id="s",
                reporting_period="p",
                financial_metrics=FinancialMetricsInput(
                    total_spend=Decimal("100"),
                    total_waste_amount=Decimal("10"),
                    waste_percentage=Decimal("10"),
                    categories=(
                        __import__(
                            "app.business.engines.risk.input",
                            fromlist=["WasteCategoryMetric"],
                        ).WasteCategoryMetric("a", Decimal("10"), Decimal("100")),
                    ),
                ),
            ),
            ValidationError,
        ),
        (
            RiskEngineInput(
                organization_id="o",
                snapshot_id="s",
                reporting_period="p",
                financial_metrics=FinancialMetricsInput(
                    total_spend=Decimal("0"),
                    total_waste_amount=Decimal("0"),
                    waste_percentage=Decimal("0"),
                    categories=(),
                ),
            ),
            ValidationError,
        ),
        ("not-input", InvalidInputError),
    ],
)
def test_risk_engine_validation_errors(input_data, expected) -> None:
    engine = RiskEngine()
    with pytest.raises(expected):
        engine.run(input_data)


def test_risk_engine_waste_exceeds_spend() -> None:
    engine = RiskEngine()
    input_data = RiskEngineInput(
        organization_id="org",
        snapshot_id="snap",
        reporting_period="2026-Q2",
        financial_metrics=FinancialMetricsInput(
            total_spend=Decimal("100"),
            total_waste_amount=Decimal("200"),
            waste_percentage=Decimal("200"),
            categories=(
                __import__(
                    "app.business.engines.risk.input", fromlist=["WasteCategoryMetric"]
                ).WasteCategoryMetric("x", Decimal("200"), Decimal("100")),
            ),
        ),
        generated_at=datetime(2026, 7, 16, tzinfo=UTC),
    )
    with pytest.raises(BusinessRuleViolationError):
        engine.run(input_data)


def test_risk_engine_missing_categories() -> None:
    engine = RiskEngine()
    input_data = sample_risk_input()
    broken = RiskEngineInput(
        organization_id=input_data.organization_id,
        snapshot_id=input_data.snapshot_id,
        reporting_period=input_data.reporting_period,
        financial_metrics=FinancialMetricsInput(
            total_spend=Decimal("100"),
            total_waste_amount=Decimal("10"),
            waste_percentage=Decimal("10"),
            categories=(),
        ),
    )
    with pytest.raises(MissingDataError):
        engine.run(broken)
