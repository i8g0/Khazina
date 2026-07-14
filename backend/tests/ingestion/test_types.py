"""Unit tests for parsed dataset immutability and payload."""

from __future__ import annotations

from app.ingestion.types import ParsedDataset, ParsedRow, ParsedSheet


def test_parsed_dataset_payload_shape() -> None:
    sheet = ParsedSheet(
        name="Sheet1",
        columns=("category", "amount"),
        rows=(ParsedRow(row_number=2, values={"category": "Travel", "amount": "10"}),),
    )
    dataset = ParsedDataset(source_file_name="test.csv", sheets=(sheet,))
    payload = dataset.to_payload()
    assert payload["source_file_name"] == "test.csv"
    assert payload["sheets"][0]["name"] == "Sheet1"
    assert payload["sheets"][0]["rows"][0]["row_number"] == 2
    assert dataset.record_count == 1
