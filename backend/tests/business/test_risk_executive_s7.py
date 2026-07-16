"""Sprint 7 — Arabic executive risk findings."""

from __future__ import annotations

from tests.business.risk_conftest import sample_risk_input


def test_risk_findings_are_arabic_executive() -> None:
    from app.business.engines.risk.engine import RiskEngine

    output = RiskEngine().run(sample_risk_input())
    assert output.findings
    for finding in output.findings:
        assert finding.name, "finding must have Arabic title"
        # No English template titles from Sprint 6
        assert "Elevated" not in finding.name
        assert "Moderate" not in finding.name
        assert "exposure" not in finding.name.lower()
        assert finding.evidence.get("department_ar")
        assert finding.evidence.get("amount_exposed_sar")
        assert finding.evidence.get("executive_summary_ar")
        assert finding.evidence.get("recommended_action_ar")
        assert finding.evidence.get("detection_reason_ar")
        assert finding.evidence.get("financial_impact_ar")
        assert finding.evidence.get("waste_value_label")
