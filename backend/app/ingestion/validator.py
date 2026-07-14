"""Structural and semantic validation on parsed datasets."""

from __future__ import annotations

import re
from datetime import datetime

from app.ingestion.types import ParsedDataset, ValidationIssue, ValidationResult

_DATE_PATTERNS = (
    re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    re.compile(r"^\d{2}/\d{2}/\d{4}$"),
    re.compile(r"^\d{2}-\d{2}-\d{4}$"),
)
_AMOUNT_HINTS = ("amount", "total", "cost", "budget", "spend", "مبلغ", "تكلفة")
_DATE_HINTS = ("date", "تاريخ", "period", "فترة")


class DatasetValidator:
    """Enforces validation dimensions from AI_ARCHITECTURE.md §6."""

    def validate(self, dataset: ParsedDataset) -> ValidationResult:
        issues: list[ValidationIssue] = []
        if dataset.record_count == 0:
            issues.append(
                ValidationIssue(
                    location=dataset.source_file_name,
                    message="Dataset contains no records",
                )
            )
        for sheet in dataset.sheets:
            if not sheet.columns:
                issues.append(
                    ValidationIssue(
                        location=f"{dataset.source_file_name}/{sheet.name}",
                        message="Missing column headers",
                    )
                )
            for row in sheet.rows:
                if not any(value not in (None, "") for value in row.values.values()):
                    issues.append(
                        ValidationIssue(
                            location=(
                                f"{dataset.source_file_name}/{sheet.name}/row {row.row_number}"
                            ),
                            message="Row is entirely empty",
                        )
                    )
                for column, value in row.values.items():
                    if value is None or value == "":
                        continue
                    if self._is_amount_column(column) and not self._is_numeric(value):
                        issues.append(
                            ValidationIssue(
                                location=(
                                    f"{dataset.source_file_name}/{sheet.name}/row {row.row_number}"
                                ),
                                message=f"Non-numeric amount in column '{column}'",
                            )
                        )
                    if self._is_date_column(column) and not self._is_valid_date(value):
                        issues.append(
                            ValidationIssue(
                                location=(
                                    f"{dataset.source_file_name}/{sheet.name}/row {row.row_number}"
                                ),
                                message=f"Invalid date format in column '{column}'",
                            )
                        )
        return ValidationResult(is_valid=not issues, issues=tuple(issues))

    @staticmethod
    def _is_amount_column(column: str) -> bool:
        lowered = column.lower()
        return any(hint in lowered for hint in _AMOUNT_HINTS)

    @staticmethod
    def _is_date_column(column: str) -> bool:
        lowered = column.lower()
        return any(hint in lowered for hint in _DATE_HINTS)

    @staticmethod
    def _is_numeric(value: str) -> bool:
        cleaned = value.replace(",", "").replace(" ", "").strip()
        if cleaned.endswith("%"):
            cleaned = cleaned[:-1]
        try:
            float(cleaned)
        except ValueError:
            return False
        return True

    @staticmethod
    def _is_valid_date(value: str) -> bool:
        if any(pattern.match(value) for pattern in _DATE_PATTERNS):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    datetime.strptime(value, fmt)
                    return True
                except ValueError:
                    continue
        return False
