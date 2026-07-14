"""Waste v1 Snapshot-to-Engine Input Adapter (§11 approved contract)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from app.business.engines.waste.input import WasteCategoryInput, WasteEngineInput
from app.decision.constants import (
    ACTUAL_SUM_ALIASES,
    BUDGET_SUM_ALIASES,
    CATEGORY_ALIASES,
    SCHEMA_V1_REQUIRED_KEYS,
    SOURCE_DATASET_FINANCIAL_SNAPSHOT_V1,
    TOTAL_SPEND_FIXED_ALIASES,
    WASTE_AMOUNT_ALIASES,
)
from app.decision.exceptions import SnapshotAdapterError


def _normalize_header(header: str) -> str:
    return header.strip().casefold()


def _header_matches_alias(header: str, alias: str) -> bool:
    return _normalize_header(header) == _normalize_header(alias)


def _match_columns(columns: tuple[str, ...], aliases: frozenset[str]) -> list[str]:
    matched: list[str] = []
    for column in columns:
        if any(_header_matches_alias(column, alias) for alias in aliases):
            matched.append(column)
    return matched


@dataclass(frozen=True, slots=True)
class _SheetResolution:
    sheet_name: str
    category_column: str
    waste_amount_column: str
    denominator_path: str
    denominator_column: str


class WasteSnapshotAdapterV1:
    """Maps Financial Snapshot schema v1 payload to ``WasteEngineInput``."""

    def adapt(
        self,
        payload: dict[str, Any],
        *,
        organization_id: str | None = None,
        period: str | None = None,
        generated_at: datetime | None = None,
    ) -> WasteEngineInput:
        self._validate_schema(payload)
        sheets = payload["sheets"]
        resolution = self._select_sheet_resolution(sheets)
        sheet = next(s for s in sheets if s.get("name") == resolution.sheet_name)
        categories = self._aggregate_categories(sheet, resolution)
        total_waste = self._money(sum(item.amount for item in categories))
        total_spend = self._resolve_total_spend(sheet, resolution)

        if total_spend <= 0:
            raise SnapshotAdapterError(
                "invalid_total_spend",
                "Total spend must be greater than zero",
                {"sheet": resolution.sheet_name},
            )
        if total_waste <= 0:
            raise SnapshotAdapterError(
                "no_waste_categories",
                "At least one waste category with a positive amount is required",
                {"sheet": resolution.sheet_name},
            )
        if total_waste > total_spend:
            raise SnapshotAdapterError(
                "waste_exceeds_spend",
                "Total waste amount must not exceed total spend",
                {
                    "sheet": resolution.sheet_name,
                    "total_waste_amount": str(total_waste),
                    "total_spend": str(total_spend),
                },
            )

        timestamp = generated_at or datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        sorted_categories = tuple(
            sorted(categories, key=lambda item: item.category_name)
        )
        return WasteEngineInput(
            total_spend=float(total_spend),
            total_waste_amount=float(total_waste),
            categories=sorted_categories,
            organization_id=organization_id,
            period=period,
            source_dataset=SOURCE_DATASET_FINANCIAL_SNAPSHOT_V1,
            generated_at=timestamp,
        )

    @staticmethod
    def _validate_schema(payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise SnapshotAdapterError(
                "invalid_snapshot_schema",
                "Snapshot payload must be an object",
            )
        missing = SCHEMA_V1_REQUIRED_KEYS - payload.keys()
        if missing:
            raise SnapshotAdapterError(
                "invalid_snapshot_schema",
                "Snapshot payload missing required keys",
                {"missing_keys": sorted(missing)},
            )
        if not isinstance(payload["sheets"], list):
            raise SnapshotAdapterError(
                "invalid_snapshot_schema",
                "Snapshot sheets must be a list",
            )

    def _qualifying_sheets(
        self, sheets: list[Any]
    ) -> tuple[list[_SheetResolution], list[SnapshotAdapterError]]:
        qualifying: list[_SheetResolution] = []
        resolution_errors: list[SnapshotAdapterError] = []
        for sheet in sheets:
            if not isinstance(sheet, dict):
                continue
            name = str(sheet.get("name", ""))
            columns = tuple(sheet.get("columns") or [])
            if not columns:
                continue
            try:
                resolution = self._resolve_sheet(name, columns)
            except SnapshotAdapterError as exc:
                resolution_errors.append(exc)
                continue
            qualifying.append(resolution)
        return qualifying, resolution_errors

    def _select_sheet_resolution(
        self, sheets: list[Any]
    ) -> _SheetResolution:
        qualifying, resolution_errors = self._qualifying_sheets(sheets)
        if len(qualifying) == 1:
            return qualifying[0]
        if len(qualifying) > 1:
            raise SnapshotAdapterError(
                "ambiguous_layout",
                "More than one sheet qualifies for Waste layout W-1",
                {"qualifying_sheet_names": [r.sheet_name for r in qualifying]},
            )
        if len(sheets) == 1 and len(resolution_errors) == 1:
            raise resolution_errors[0]
        raise SnapshotAdapterError(
            "unsupported_layout",
            "No sheet qualifies for Waste layout W-1",
            {"sheet_names": [s.get("name", "") for s in sheets if isinstance(s, dict)]},
        )

    def _resolve_sheet(self, sheet_name: str, columns: tuple[str, ...]) -> _SheetResolution:
        category_matches = _match_columns(columns, CATEGORY_ALIASES)
        waste_matches = _match_columns(columns, WASTE_AMOUNT_ALIASES)

        if len(category_matches) == 0:
            raise SnapshotAdapterError(
                "missing_required_column",
                "Required column not found",
                {"sheet": sheet_name, "semantic_role": "category"},
            )
        if len(category_matches) > 1:
            raise SnapshotAdapterError(
                "ambiguous_column_mapping",
                "Multiple columns match semantic role",
                {
                    "sheet": sheet_name,
                    "semantic_role": "category",
                    "matching_headers": category_matches,
                },
            )
        if len(waste_matches) == 0:
            raise SnapshotAdapterError(
                "missing_required_column",
                "Required column not found",
                {"sheet": sheet_name, "semantic_role": "waste_amount"},
            )
        if len(waste_matches) > 1:
            raise SnapshotAdapterError(
                "ambiguous_column_mapping",
                "Multiple columns match semantic role",
                {
                    "sheet": sheet_name,
                    "semantic_role": "waste_amount",
                    "matching_headers": waste_matches,
                },
            )

        denominator_path, denominator_column = self._resolve_denominator(
            sheet_name, columns
        )
        return _SheetResolution(
            sheet_name=sheet_name,
            category_column=category_matches[0],
            waste_amount_column=waste_matches[0],
            denominator_path=denominator_path,
            denominator_column=denominator_column,
        )

    def _resolve_denominator(
        self, sheet_name: str, columns: tuple[str, ...]
    ) -> tuple[str, str]:
        fixed_matches = _match_columns(columns, TOTAL_SPEND_FIXED_ALIASES)
        budget_matches = _match_columns(columns, BUDGET_SUM_ALIASES)
        actual_matches = _match_columns(columns, ACTUAL_SUM_ALIASES)

        active_paths: list[tuple[str, list[str]]] = []
        if fixed_matches:
            active_paths.append(("total_spend_fixed", fixed_matches))
        if budget_matches:
            active_paths.append(("budget", budget_matches))
        if actual_matches:
            active_paths.append(("actual", actual_matches))

        if not active_paths:
            raise SnapshotAdapterError(
                "missing_denominator_column",
                "No denominator column found",
                {
                    "sheet": sheet_name,
                    "accepted_paths": [
                        "total_spend_fixed",
                        "budget",
                        "actual",
                    ],
                },
            )
        if len(active_paths) > 1:
            raise SnapshotAdapterError(
                "ambiguous_column_mapping",
                "Multiple denominator paths match",
                {
                    "sheet": sheet_name,
                    "conflicting_paths": [path for path, _ in active_paths],
                },
            )

        path_name, path_matches = active_paths[0]
        if len(path_matches) > 1:
            raise SnapshotAdapterError(
                "ambiguous_column_mapping",
                "Multiple columns match denominator semantic role",
                {
                    "sheet": sheet_name,
                    "semantic_role": path_name,
                    "matching_headers": path_matches,
                },
            )
        return path_name, path_matches[0]

    def _aggregate_categories(
        self, sheet: dict[str, Any], resolution: _SheetResolution
    ) -> tuple[WasteCategoryInput, ...]:
        rows = sheet.get("rows") or []
        aggregates: dict[str, tuple[str, Decimal]] = {}
        order: list[str] = []

        for row in rows:
            if not isinstance(row, dict):
                continue
            values = row.get("values") or {}
            if not isinstance(values, dict):
                continue
            if not any(v not in (None, "") for v in values.values()):
                continue

            raw_category = values.get(resolution.category_column)
            category_key = str(raw_category or "").strip()
            if not category_key:
                row_number = row.get("row_number")
                raise SnapshotAdapterError(
                    "empty_category",
                    "Category must not be empty",
                    {
                        "sheet": resolution.sheet_name,
                        "row_number": row_number,
                    },
                )

            raw_amount = values.get(resolution.waste_amount_column)
            if raw_amount is None or raw_amount == "":
                continue

            amount = self._parse_amount(
                raw_amount,
                sheet=resolution.sheet_name,
                row_number=row.get("row_number"),
            )
            if category_key not in aggregates:
                aggregates[category_key] = (category_key, Decimal("0.00"))
                order.append(category_key)
            label, running = aggregates[category_key]
            aggregates[category_key] = (label, running + amount)

        if not aggregates:
            raise SnapshotAdapterError(
                "no_waste_categories",
                "No waste categories found after row filtering",
                {"sheet": resolution.sheet_name},
            )

        return tuple(
            WasteCategoryInput(
                category_name=aggregates[key][0],
                amount=float(aggregates[key][1]),
            )
            for key in order
            if aggregates[key][1] > 0
        )

    def _resolve_total_spend(
        self, sheet: dict[str, Any], resolution: _SheetResolution
    ) -> Decimal:
        rows = sheet.get("rows") or []
        column = resolution.denominator_column

        if resolution.denominator_path == "total_spend_fixed":
            distinct: set[Decimal] = set()
            for row in rows:
                if not isinstance(row, dict):
                    continue
                values = row.get("values") or {}
                raw = values.get(column)
                if raw is None or raw == "":
                    continue
                distinct.add(
                    self._parse_amount(
                        raw,
                        sheet=resolution.sheet_name,
                        row_number=row.get("row_number"),
                    )
                )
            if len(distinct) != 1:
                raise SnapshotAdapterError(
                    "ambiguous_total_spend",
                    "Fixed total spend must have exactly one distinct positive value",
                    {
                        "sheet": resolution.sheet_name,
                        "distinct_value_count": len(distinct),
                    },
                )
            return next(iter(distinct))

        total = Decimal("0.00")
        for row in rows:
            if not isinstance(row, dict):
                continue
            values = row.get("values") or {}
            raw = values.get(column)
            if raw is None or raw == "":
                continue
            total += self._parse_amount(
                raw,
                sheet=resolution.sheet_name,
                row_number=row.get("row_number"),
            )
        return self._money(total)

    def _parse_amount(
        self, raw: Any, *, sheet: str, row_number: Any
    ) -> Decimal:
        if not isinstance(raw, str):
            raw = str(raw)
        cleaned = raw.replace(",", "").replace(" ", "").strip()
        if cleaned.endswith("%"):
            cleaned = cleaned[:-1]
        try:
            value = Decimal(cleaned)
        except Exception as exc:
            raise SnapshotAdapterError(
                "invalid_waste_amount",
                "Non-numeric amount value",
                {"sheet": sheet, "row_number": row_number, "value": raw},
            ) from exc
        if value < 0:
            raise SnapshotAdapterError(
                "invalid_waste_amount",
                "Amount must not be negative",
                {"sheet": sheet, "row_number": row_number, "value": raw},
            )
        return self._money(value)

    @staticmethod
    def _money(value: Decimal | float) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
