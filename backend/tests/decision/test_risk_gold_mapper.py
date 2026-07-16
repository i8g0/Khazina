"""Unit tests for Risk Gold mapper."""

from __future__ import annotations

import uuid

import pytest

from app.business.bootstrap import initialize_business_engines
from app.business.engines.risk import RiskEngine
from app.decision.mappers.risk_gold import RiskGoldMapper
from tests.business.risk_conftest import sample_risk_input


@pytest.fixture
def business_engines_initialized() -> None:
    initialize_business_engines()


def test_risk_gold_mapper_maps_engine_output(
    business_engines_initialized: None,
) -> None:
    output = RiskEngine().run(sample_risk_input())
    org_id = uuid.uuid4()
    run_id = uuid.uuid4()
    snapshot_id = uuid.uuid4()

    payload = RiskGoldMapper.to_persistence_payload(
        output,
        organization_id=org_id,
        analysis_run_id=run_id,
        source_snapshot_id=snapshot_id,
    )

    result = payload["result"]
    assert result["analysis_run_id"] == run_id
    assert result["organization_id"] == org_id
    assert result["source_snapshot_id"] == snapshot_id
    assert result["total_findings"] == len(output.findings)
    assert result["high_priority_count"] == output.detection.high_count
    assert result["overall_posture_level"] == output.detection.overall_posture_level
    assert result["facts_contract_version"] == output.facts_contract.contract_version

    findings = payload["findings"]
    assert len(findings) == len(output.findings)
    for row, engine_finding in zip(findings, output.findings, strict=True):
        assert isinstance(row["id"], uuid.UUID)
        assert row["id"] != uuid.UUID(engine_finding.finding_id)
        assert row["evidence"]["engine_finding_id"] == engine_finding.finding_id
        assert row["analysis_run_id"] == run_id
        assert row["organization_id"] == org_id
        assert row["category_code"] == engine_finding.category_code
        assert row["score"] == engine_finding.score
        assert row["finding_status"] == "detected"
        assert row["promoted_risk_id"] is None

    if output.findings:
        assert result["top_category_code"] == output.findings[0].category_code
    else:
        assert result["top_category_code"] is None


def test_risk_gold_mapper_preserves_engine_finding_ids_in_evidence(
    business_engines_initialized: None,
) -> None:
    engine = RiskEngine()
    first = RiskGoldMapper.to_persistence_payload(
        engine.run(sample_risk_input()),
        organization_id=uuid.uuid4(),
        analysis_run_id=uuid.uuid4(),
        source_snapshot_id=uuid.uuid4(),
    )
    second = RiskGoldMapper.to_persistence_payload(
        engine.run(sample_risk_input()),
        organization_id=uuid.uuid4(),
        analysis_run_id=uuid.uuid4(),
        source_snapshot_id=uuid.uuid4(),
    )
    assert [row["evidence"]["engine_finding_id"] for row in first["findings"]] == [
        row["evidence"]["engine_finding_id"] for row in second["findings"]
    ]
    assert [row["id"] for row in first["findings"]] != [
        row["id"] for row in second["findings"]
    ]
