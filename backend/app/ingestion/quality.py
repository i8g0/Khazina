"""Data quality assessment for repository-level checks."""

from __future__ import annotations

import json

from app.ingestion.constants import (
    CHECK_BUDGET_ALIGNMENT,
    CHECK_DATE_FORMAT,
    CHECK_DUPLICATE_RECORDS,
    CHECK_FIELD_COMPLETENESS,
)
from app.ingestion.types import ParsedDataset, QualityAssessment, QualityCheckResult


class DatasetQualityAssessor:
    """Produces the four placeholder validation categories."""

    def assess(self, dataset: ParsedDataset) -> QualityAssessment:
        checks = (
            self._field_completeness(dataset),
            self._budget_alignment(dataset),
            self._date_format(dataset),
            self._duplicate_records(dataset),
        )
        overall = round(sum(check.result_percent for check in checks) / len(checks), 2)
        return QualityAssessment(overall_score=overall, checks=checks)

    def _field_completeness(self, dataset: ParsedDataset) -> QualityCheckResult:
        total_cells = 0
        filled_cells = 0
        missing_classification = 0
        for sheet in dataset.sheets:
            for row in sheet.rows:
                for column, value in row.values.items():
                    total_cells += 1
                    if value not in (None, ""):
                        filled_cells += 1
                    if "category" in column.lower() or "تصنيف" in column:
                        if value in (None, ""):
                            missing_classification += 1
        percent = 100.0 if total_cells == 0 else round(100 * filled_cells / total_cells, 2)
        details = (
            f"{missing_classification} سجل بدون تصنيف"
            if missing_classification
            else None
        )
        return QualityCheckResult(
            check_name=CHECK_FIELD_COMPLETENESS,
            result_percent=percent,
            details=details,
            display_order=0,
        )

    def _budget_alignment(self, dataset: ParsedDataset) -> QualityCheckResult:
        violations = 0
        checked = 0
        for sheet in dataset.sheets:
            for row in sheet.rows:
                budget = row.values.get("budget") or row.values.get("الميزانية")
                actual = row.values.get("actual") or row.values.get("amount")
                if budget is None or actual is None:
                    continue
                checked += 1
                try:
                    budget_value = float(str(budget).replace(",", ""))
                    actual_value = float(str(actual).replace(",", ""))
                except ValueError:
                    continue
                if actual_value > budget_value:
                    violations += 1
        if checked == 0:
            percent = 100.0
            details = None
        else:
            percent = round(100 * (checked - violations) / checked, 2)
            details = f"{violations} تجاوزات" if violations else None
        return QualityCheckResult(
            check_name=CHECK_BUDGET_ALIGNMENT,
            result_percent=percent,
            details=details,
            display_order=1,
        )

    def _date_format(self, dataset: ParsedDataset) -> QualityCheckResult:
        total_dates = 0
        valid_dates = 0
        for sheet in dataset.sheets:
            for row in sheet.rows:
                for column, value in row.values.items():
                    if value in (None, ""):
                        continue
                    if "date" not in column.lower() and "تاريخ" not in column:
                        continue
                    total_dates += 1
                    if self._looks_like_date(value):
                        valid_dates += 1
        percent = 100.0 if total_dates == 0 else round(100 * valid_dates / total_dates, 2)
        return QualityCheckResult(
            check_name=CHECK_DATE_FORMAT,
            result_percent=percent,
            details=None,
            display_order=2,
        )

    def _duplicate_records(self, dataset: ParsedDataset) -> QualityCheckResult:
        seen: set[str] = set()
        duplicates = 0
        total = dataset.record_count
        for sheet in dataset.sheets:
            for row in sheet.rows:
                fingerprint = json.dumps(row.values, sort_keys=True, ensure_ascii=False)
                if fingerprint in seen:
                    duplicates += 1
                seen.add(fingerprint)
        percent = 100.0 if total == 0 else round(100 * (total - duplicates) / total, 2)
        details = f"{duplicates} سجل مكرر" if duplicates else None
        return QualityCheckResult(
            check_name=CHECK_DUPLICATE_RECORDS,
            result_percent=percent,
            details=details,
            display_order=3,
        )

    @staticmethod
    def _looks_like_date(value: str) -> bool:
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                from datetime import datetime

                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        return False
