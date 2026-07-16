"""Risk v1 Snapshot adapter unit tests."""

from __future__ import annotations

from app.decision.adapters.risk_v1 import RiskSnapshotAdapterV1
from tests.decision.conftest import sample_waste_payload


def test_adapt_valid_w1_payload() -> None:
    adapter = RiskSnapshotAdapterV1()
    result = adapter.adapt(
        sample_waste_payload(),
        organization_id="org-1",
        snapshot_id="snap-1",
        period="2026-Q2",
    )

    assert result.organization_id == "org-1"
    assert result.snapshot_id == "snap-1"
    assert result.reporting_period == "2026-Q2"
    assert result.financial_metrics.total_spend == __import__(
        "decimal"
    ).Decimal("50000000.00")
    assert len(result.financial_metrics.categories) == 3
    assert result.financial_metrics.waste_percentage > 0
