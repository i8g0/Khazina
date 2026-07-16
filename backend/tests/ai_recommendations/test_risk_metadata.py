"""Risk metadata supplement tests."""

from __future__ import annotations

from app.ai_recommendations.risk_metadata import build_risk_metadata_supplement
from tests.ai_recommendations.risk_conftest import sample_risk_runtime_metadata


def test_build_risk_metadata_supplement_includes_findings() -> None:
    metadata = sample_risk_runtime_metadata()
    supplement = build_risk_metadata_supplement(metadata)
    assert "سياق التحليل المالي الحتمي" in supplement
    assert "مستشار استراتيجي" in supplement
    assert str(metadata["risk_analysis"]["overall_posture_level"]) in supplement
    assert metadata["risk_findings"][0]["name"] in supplement
