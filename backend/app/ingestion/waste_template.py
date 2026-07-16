"""Approved financial waste template (W-1) validation at ingest time."""

from __future__ import annotations

from app.decision.adapters.waste_v1 import WasteSnapshotAdapterV1
from app.decision.exceptions import SnapshotAdapterError
from app.ingestion.exceptions import ValidationFailure
from app.ingestion.types import ParsedDataset


def validate_waste_template(dataset: ParsedDataset) -> None:
    """Ensure the workbook matches layout W-1 before marking ready for analysis.

    Reuses the production WasteSnapshotAdapterV1 contract — no duplicate rules.
    Row-level and column-level failures are rejected here with clear messages
    instead of deferring failure to the waste decision step.
    """
    adapter = WasteSnapshotAdapterV1()
    try:
        adapter.adapt(dataset.to_payload())
    except SnapshotAdapterError as exc:
        raise ValidationFailure(
            "Workbook does not match the approved financial waste template (W-1): "
            f"{exc.message}"
        ) from exc
