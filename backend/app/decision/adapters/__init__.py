"""Snapshot-to-Engine input adapters."""

from app.decision.adapters.risk_v1 import RiskSnapshotAdapterV1
from app.decision.adapters.waste_v1 import WasteSnapshotAdapterV1

__all__ = ["RiskSnapshotAdapterV1", "WasteSnapshotAdapterV1"]
