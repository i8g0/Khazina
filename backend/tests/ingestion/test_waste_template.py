"""Tests for W-1 template validation at ingest."""

from __future__ import annotations

import pytest

from app.ingestion.exceptions import ValidationFailure
from app.ingestion.types import ParsedDataset, ParsedRow, ParsedSheet
from app.ingestion.waste_template import validate_waste_template


def _w1_dataset(
    *,
    file_name: str = "workbook.xlsx",
    sheet_name: str = "Data",
    rows: list[tuple[str, int, int]],
    columns: tuple[str, str, str] = ("category", "amount", "total_spend"),
) -> ParsedDataset:
    parsed_rows = tuple(
        ParsedRow(
            row_number=index + 2,
            values={
                columns[0]: category,
                columns[1]: str(amount),
                columns[2]: str(total_spend),
            },
        )
        for index, (category, amount, total_spend) in enumerate(rows)
    )
    sheet = ParsedSheet(name=sheet_name, columns=columns, rows=parsed_rows)
    return ParsedDataset(source_file_name=file_name, sheets=(sheet,))


def test_validate_accepts_canonical_w1() -> None:
    dataset = _w1_dataset(
        rows=[
            ("overlapping_contracts", 745_000, 50_000_000),
            ("operations", 520_000, 50_000_000),
            ("finance", 1_075_000, 50_000_000),
        ]
    )
    validate_waste_template(dataset)


def test_validate_accepts_arabic_headers() -> None:
    dataset = _w1_dataset(
        columns=("تصنيف", "مبلغ", "إجمالي_الإنفاق"),
        rows=[
            ("operations", 500_000, 40_000_000),
            ("finance", 600_000, 40_000_000),
        ],
    )
    validate_waste_template(dataset)


def test_validate_accepts_reordered_rows() -> None:
    dataset = _w1_dataset(
        rows=[
            ("finance", 1_075_000, 50_000_000),
            ("overlapping_contracts", 745_000, 50_000_000),
            ("operations", 520_000, 50_000_000),
        ]
    )
    validate_waste_template(dataset)


def test_validate_accepts_extended_row_count() -> None:
    dataset = _w1_dataset(
        rows=[
            ("overlapping_contracts", 100_000, 10_000_000),
            ("operations", 200_000, 10_000_000),
            ("finance", 300_000, 10_000_000),
            ("procurement", 150_000, 10_000_000),
            ("travel", 50_000, 10_000_000),
        ]
    )
    validate_waste_template(dataset)


def test_validate_rejects_non_w1_layout() -> None:
    dataset = ParsedDataset(
        source_file_name="generic.xlsx",
        sheets=(
            ParsedSheet(
                name="Budget",
                columns=("department", "budget", "actual"),
                rows=(
                    ParsedRow(
                        row_number=2,
                        values={"department": "IT", "budget": "100", "actual": "90"},
                    ),
                ),
            ),
        ),
    )
    with pytest.raises(ValidationFailure, match="approved financial waste template"):
        validate_waste_template(dataset)


def test_validate_rejects_invalid_amount() -> None:
    dataset = _w1_dataset(rows=[("operations", "not-a-number", 50_000_000)])
    with pytest.raises(ValidationFailure):
        validate_waste_template(dataset)
