"""Internal structures for the Financial Snapshot contract (schema v1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ParsedRow:
    """Single normalized row from a spreadsheet sheet."""

    row_number: int
    values: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ParsedSheet:
    """Normalized sheet with column names and row records."""

    name: str
    columns: tuple[str, ...]
    rows: tuple[ParsedRow, ...]


@dataclass(frozen=True, slots=True)
class ParsedDataset:
    """Internal structure v1 — cohesive snapshot payload."""

    source_file_name: str
    sheets: tuple[ParsedSheet, ...]

    @property
    def record_count(self) -> int:
        return sum(len(sheet.rows) for sheet in self.sheets)

    def to_payload(self) -> dict[str, Any]:
        return {
            "source_file_name": self.source_file_name,
            "sheets": [
                {
                    "name": sheet.name,
                    "columns": list(sheet.columns),
                    "rows": [
                        {"row_number": row.row_number, "values": row.values}
                        for row in sheet.rows
                    ],
                }
                for sheet in self.sheets
            ],
        }


@dataclass(frozen=True, slots=True)
class ParseMetadata:
    """Parse metadata stored on financial_files.metadata — not snapshot body."""

    column_mappings: dict[str, list[str]]
    sheet_names: list[str]
    row_counts: dict[str, int]
    parser_version: str
    schema_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "column_mappings": self.column_mappings,
            "sheet_names": self.sheet_names,
            "row_counts": self.row_counts,
            "parser_version": self.parser_version,
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class ValidationResult:
    is_valid: bool
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)

    @property
    def error_message(self) -> str:
        if self.is_valid:
            return ""
        return "; ".join(f"{issue.location}: {issue.message}" for issue in self.issues)


@dataclass(frozen=True, slots=True)
class QualityCheckResult:
    check_name: str
    result_percent: float
    details: str | None
    display_order: int


@dataclass(frozen=True, slots=True)
class QualityAssessment:
    overall_score: float
    checks: tuple[QualityCheckResult, ...]


@dataclass(frozen=True, slots=True)
class IngestionResult:
    """Outcome of a successful ingestion pipeline run."""

    record_count: int
    parse_metadata: ParseMetadata
    dataset: ParsedDataset
    validation: ValidationResult
    quality: QualityAssessment
