"""Optional waste Decision Result baseline cross-check."""

from __future__ import annotations

from decimal import Decimal

from app.business.facts.contract import FactsContract
from app.decision.exceptions import SnapshotAdapterError
from app.scenario.constants import BASELINE_MISMATCH_TOLERANCE


def validate_waste_baseline_alignment(
    *,
    snapshot_baseline_total: float,
    facts_contract: FactsContract,
) -> None:
    """Read-only cross-check between snapshot baseline and waste facts."""
    by_metric = {fact.metric: fact for fact in facts_contract.facts}
    waste_total = by_metric.get("waste.total_amount")
    waste_pct = by_metric.get("waste.percentage")
    if waste_total is None or waste_pct is None:
        raise SnapshotAdapterError(
            "baseline_cross_check_failed",
            "Waste facts contract missing required waste metrics for cross-check",
        )
    pct = Decimal(waste_pct.value)
    if pct <= 0:
        raise SnapshotAdapterError(
            "baseline_cross_check_failed",
            "Waste percentage must be positive for baseline cross-check",
        )
    implied_spend = Decimal(waste_total.value) / (pct / Decimal("100"))
    snapshot_total = Decimal(str(snapshot_baseline_total))
    if snapshot_total <= 0:
        raise SnapshotAdapterError(
            "baseline_cross_check_failed",
            "Snapshot baseline total must be positive for cross-check",
        )
    delta_ratio = abs(implied_spend - snapshot_total) / snapshot_total
    if delta_ratio > Decimal(str(BASELINE_MISMATCH_TOLERANCE)):
        raise SnapshotAdapterError(
            "baseline_mismatch",
            "Snapshot baseline diverges from waste decision result beyond tolerance",
            {
                "snapshot_baseline_total": str(snapshot_total),
                "implied_spend_from_waste": str(implied_spend.quantize(Decimal("0.01"))),
                "tolerance": BASELINE_MISMATCH_TOLERANCE,
            },
        )
