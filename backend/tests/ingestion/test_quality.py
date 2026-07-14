"""Unit tests for data quality assessment."""

from __future__ import annotations

from app.ingestion.constants import (
    CHECK_BUDGET_ALIGNMENT,
    CHECK_DATE_FORMAT,
    CHECK_DUPLICATE_RECORDS,
    CHECK_FIELD_COMPLETENESS,
)
from app.ingestion.quality import DatasetQualityAssessor
from app.ingestion.types import ParsedDataset, ParsedRow, ParsedSheet


def test_assess_produces_four_checks() -> None:
    sheet = ParsedSheet(
        name="Sheet1",
        columns=("category", "amount", "date", "budget", "actual"),
        rows=(
            ParsedRow(
                row_number=2,
                values={
                    "category": "Travel",
                    "amount": "100",
                    "date": "2026-06-01",
                    "budget": "200",
                    "actual": "100",
                },
            ),
            ParsedRow(
                row_number=3,
                values={
                    "category": "Travel",
                    "amount": "100",
                    "date": "2026-06-02",
                    "budget": "200",
                    "actual": "100",
                },
            ),
        ),
    )
    dataset = ParsedDataset(source_file_name="procurement.csv", sheets=(sheet,))
    assessment = DatasetQualityAssessor().assess(dataset)
    names = {check.check_name for check in assessment.checks}
    assert names == {
        CHECK_FIELD_COMPLETENESS,
        CHECK_BUDGET_ALIGNMENT,
        CHECK_DATE_FORMAT,
        CHECK_DUPLICATE_RECORDS,
    }
    assert 0 <= assessment.overall_score <= 100
