"""Unit tests for Waste v1 Snapshot adapter."""

from __future__ import annotations

import pytest

from app.decision.adapters.waste_v1 import WasteSnapshotAdapterV1
from app.decision.exceptions import SnapshotAdapterError
from tests.decision.conftest import sample_waste_payload


def test_adapt_valid_w1_payload() -> None:
    adapter = WasteSnapshotAdapterV1()
    result = adapter.adapt(sample_waste_payload(), organization_id="org-1", period="2026-Q2")

    assert result.total_spend == 50_000_000.0
    assert result.total_waste_amount == 2_340_000.0
    assert len(result.categories) == 3
    assert result.source_dataset == "financial_snapshot_v1"
    assert [c.category_name for c in result.categories] == sorted(
        ["overlapping_contracts", "operations", "finance"]
    )


def test_adapt_ambiguous_layout_two_qualifying_sheets() -> None:
    adapter = WasteSnapshotAdapterV1()
    with pytest.raises(SnapshotAdapterError) as exc:
        adapter.adapt(sample_waste_payload(include_second_sheet=True))
    assert exc.value.error_code == "ambiguous_layout"


def test_adapt_unsupported_layout_no_qualifying_sheet() -> None:
    adapter = WasteSnapshotAdapterV1()
    payload = {
        "source_file_name": "Budget.xlsx",
        "sheets": [
            {
                "name": "Budget",
                "columns": ["budget", "actual"],
                "rows": [{"row_number": 2, "values": {"budget": "100", "actual": "90"}}],
            },
            {
                "name": "Payroll",
                "columns": ["employee", "salary"],
                "rows": [{"row_number": 2, "values": {"employee": "a", "salary": "100"}}],
            },
        ],
    }
    with pytest.raises(SnapshotAdapterError) as exc:
        adapter.adapt(payload)
    assert exc.value.error_code == "unsupported_layout"


def test_adapt_ambiguous_column_mapping_duplicate_category_aliases() -> None:
    adapter = WasteSnapshotAdapterV1()
    payload = {
        "source_file_name": "bad.xlsx",
        "sheets": [
            {
                "name": "Sheet1",
                "columns": ["category", "type", "amount", "total_spend"],
                "rows": [
                    {
                        "row_number": 2,
                        "values": {
                            "category": "a",
                            "type": "b",
                            "amount": "100",
                            "total_spend": "1000",
                        },
                    }
                ],
            }
        ],
    }
    with pytest.raises(SnapshotAdapterError) as exc:
        adapter.adapt(payload)
    assert exc.value.error_code == "ambiguous_column_mapping"


def test_adapt_missing_denominator_column() -> None:
    adapter = WasteSnapshotAdapterV1()
    payload = {
        "source_file_name": "bad.xlsx",
        "sheets": [
            {
                "name": "Sheet1",
                "columns": ["category", "amount"],
                "rows": [
                    {"row_number": 2, "values": {"category": "a", "amount": "100"}}
                ],
            }
        ],
    }
    with pytest.raises(SnapshotAdapterError) as exc:
        adapter.adapt(payload)
    assert exc.value.error_code == "missing_denominator_column"


def test_adapt_invalid_amount_fails() -> None:
    adapter = WasteSnapshotAdapterV1()
    payload = sample_waste_payload()
    payload["sheets"][0]["rows"][0]["values"]["amount"] = "not-a-number"
    with pytest.raises(SnapshotAdapterError) as exc:
        adapter.adapt(payload)
    assert exc.value.error_code == "invalid_waste_amount"


def test_adapt_aggregates_duplicate_categories() -> None:
    adapter = WasteSnapshotAdapterV1()
    payload = sample_waste_payload()
    payload["sheets"][0]["rows"].append(
        {
            "row_number": 5,
            "values": {
                "category": "operations",
                "amount": "100000",
                "total_spend": "50000000",
            },
        }
    )
    result = adapter.adapt(payload)
    operations = next(c for c in result.categories if c.category_name == "operations")
    assert operations.amount == 620_000.0
