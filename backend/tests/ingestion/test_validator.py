"""Unit tests for dataset validation."""

from __future__ import annotations

from app.ingestion.types import ParsedDataset, ParsedRow, ParsedSheet
from app.ingestion.validator import DatasetValidator


def _dataset(*rows: dict[str, str | None]) -> ParsedDataset:
    parsed_rows = tuple(
        ParsedRow(row_number=index + 2, values=row) for index, row in enumerate(rows)
    )
    sheet = ParsedSheet(
        name="Sheet1",
        columns=tuple(rows[0].keys()) if rows else ("category", "amount"),
        rows=parsed_rows,
    )
    return ParsedDataset(source_file_name="test.csv", sheets=(sheet,))


def test_validate_accepts_valid_dataset() -> None:
    dataset = _dataset(
        {"category": "Travel", "amount": "1000", "date": "2026-06-01"},
    )
    result = DatasetValidator().validate(dataset)
    assert result.is_valid


def test_validate_rejects_non_numeric_amount() -> None:
    dataset = _dataset({"category": "Travel", "amount": "invalid", "date": "2026-06-01"})
    result = DatasetValidator().validate(dataset)
    assert not result.is_valid
    assert "Non-numeric amount" in result.error_message


def test_validate_rejects_empty_dataset() -> None:
    dataset = ParsedDataset(source_file_name="empty.csv", sheets=())
    result = DatasetValidator().validate(dataset)
    assert not result.is_valid
