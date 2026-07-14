"""Scenario v1 Snapshot-to-Baseline adapter (S-1 layout, §11 pattern)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from app.business.engines.scenario.input import ScenarioBaselineInput, ScenarioCategoryBaseline
from app.decision.exceptions import SnapshotAdapterError
from app.scenario.constants import (
    ACTUAL_SUM_ALIASES,
    BUDGET_SUM_ALIASES,
    SCHEMA_V1_REQUIRED_KEYS,
    SCENARIO_AMOUNT_ALIASES,
    SCENARIO_CATEGORY_ALIASES,
    SOURCE_DATASET_FINANCIAL_SNAPSHOT_V1,
    TOTAL_SPEND_FIXED_ALIASES,
)


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
    amount_column: str
    denominator_path: str
    denominator_column: str


class ScenarioSnapshotAdapterV1:
    """Maps Financial Snapshot schema v1 payload to ``ScenarioBaselineInput``."""

    def adapt(
        self,
        payload: dict[str, Any],
        *,
        organization_id: str | None = None,
        period: str | None = None,
        generated_at: datetime | None = None,
    ) -> ScenarioBaselineInput:
        self._validate_schema(payload)
        sheets = payload["sheets"]
        resolution = self._select_sheet_resolution(sheets)
        sheet = next(s for s in sheets if s.get("name") == resolution.sheet_name)
        categories = self._aggregate_categories(sheet, resolution)
        category_total = self._money(sum(item.amount for item in categories))
        total_baseline = self._resolve_total_baseline(sheet, resolution, category_total)

        if total_baseline <= 0:
            raise SnapshotAdapterError(
                "invalid_total_baseline",
                "Total baseline must be greater than zero",
                {"sheet": resolution.sheet_name},
            )
        if not categories:
            raise SnapshotAdapterError(
                "no_baseline_categories",
                "At least one baseline category with a positive amount is required",
                {"sheet": resolution.sheet_name},
            )

        timestamp = generated_at or datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        return ScenarioBaselineInput(
            total_baseline=float(total_baseline),
            categories=tuple(
                sorted(categories, key=lambda item: item.category_name)
            ),
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

    def _select_sheet_resolution(self, sheets: list[Any]) -> _SheetResolution:
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
                qualifying.append(self._resolve_sheet(name, columns))
            except SnapshotAdapterError as exc:
                resolution_errors.append(exc)
        if len(qualifying) == 1:
            return qualifying[0]
        if len(qualifying) > 1:
            raise SnapshotAdapterError(
                "ambiguous_layout",
                "More than one sheet qualifies for Scenario layout S-1",
                {"qualifying_sheet_names": [r.sheet_name for r in qualifying]},
            )
        if len(sheets) == 1 and len(resolution_errors) == 1:
            raise resolution_errors[0]
        raise SnapshotAdapterError(
            "unsupported_layout",
            "No sheet qualifies for Scenario layout S-1",
            {"sheet_names": [s.get("name", "") for s in sheets if isinstance(s, dict)]},
        )

    def _resolve_sheet(self, sheet_name: str, columns: tuple[str, ...]) -> _SheetResolution:
        category_matches = _match_columns(columns, SCENARIO_CATEGORY_ALIASES)
        amount_matches = _match_columns(columns, SCENARIO_AMOUNT_ALIASES)
        if len(category_matches) != 1:
            raise SnapshotAdapterError(
                "missing_required_column" if not category_matches else "ambiguous_column_mapping",
                "Category column resolution failed",
                {"sheet": sheet_name, "semantic_role": "category", "matching_headers": category_matches},
            )
        if len(amount_matches) != 1:
            raise SnapshotAdapterError(
                "missing_required_column" if not amount_matches else "ambiguous_column_mapping",
                "Amount column resolution failed",
                {"sheet": sheet_name, "semantic_role": "amount", "matching_headers": amount_matches},
            )
        denominator_path, denominator_column = self._resolve_denominator(sheet_name, columns)
        return _SheetResolution(
            sheet_name=sheet_name,
            category_column=category_matches[0],
            amount_column=amount_matches[0],
            denominator_path=denominator_path,
            denominator_column=denominator_column,
        )

    def _resolve_denominator(
        self, sheet_name: str, columns: tuple[str, ...]
    ) -> tuple[str, str]:
        paths: list[tuple[str, list[str]]] = []
        fixed = _match_columns(columns, TOTAL_SPEND_FIXED_ALIASES)
        budget = _match_columns(columns, BUDGET_SUM_ALIASES)
        actual = _match_columns(columns, ACTUAL_SUM_ALIASES)
        if fixed:
            paths.append(("total_spend_fixed", fixed))
        if budget:
            paths.append(("budget", budget))
        if actual:
            paths.append(("actual", actual))
        if not paths:
            raise SnapshotAdapterError(
                "missing_denominator_column",
                "No denominator column found",
                {"sheet": sheet_name},
            )
        if len(paths) > 1:
            raise SnapshotAdapterError(
                "ambiguous_column_mapping",
                "Multiple denominator paths match",
                {"sheet": sheet_name, "conflicting_paths": [p for p, _ in paths]},
            )
        path_name, matches = paths[0]
        if len(matches) != 1:
            raise SnapshotAdapterError(
                "ambiguous_column_mapping",
                "Multiple columns match denominator",
                {"sheet": sheet_name, "semantic_role": path_name, "matching_headers": matches},
            )
        return path_name, matches[0]

    def _aggregate_categories(
        self, sheet: dict[str, Any], resolution: _SheetResolution
    ) -> tuple[ScenarioCategoryBaseline, ...]:
        aggregates: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
        order: list[str] = []
        for row in sheet.get("rows") or []:
            if not isinstance(row, dict):
                continue
            values = row.get("values") or {}
            if not isinstance(values, dict):
                continue
            category_key = str(values.get(resolution.category_column) or "").strip()
            if not category_key:
                continue
            raw_amount = values.get(resolution.amount_column)
            if raw_amount in (None, ""):
                continue
            amount = self._parse_amount(raw_amount)
            if category_key not in order:
                order.append(category_key)
            aggregates[category_key] += amount
        return tuple(
            ScenarioCategoryBaseline(category_name=key, amount=float(aggregates[key]))
            for key in order
            if aggregates[key] > 0
        )

    def _resolve_total_baseline(
        self,
        sheet: dict[str, Any],
        resolution: _SheetResolution,
        category_total: Decimal,
    ) -> Decimal:
        if resolution.denominator_path == "total_spend_fixed":
            distinct: set[Decimal] = set()
            for row in sheet.get("rows") or []:
                if not isinstance(row, dict):
                    continue
                values = row.get("values") or {}
                raw = values.get(resolution.denominator_column)
                if raw in (None, ""):
                    continue
                distinct.add(self._parse_amount(raw))
            if len(distinct) != 1:
                raise SnapshotAdapterError(
                    "ambiguous_total_spend",
                    "Fixed total baseline must have exactly one distinct value",
                    {"sheet": resolution.sheet_name, "distinct_value_count": len(distinct)},
                )
            return next(iter(distinct))
        if category_total > 0:
            return category_total
        total = Decimal("0.00")
        for row in sheet.get("rows") or []:
            if not isinstance(row, dict):
                continue
            values = row.get("values") or {}
            raw = values.get(resolution.denominator_column)
            if raw in (None, ""):
                continue
            total += self._parse_amount(raw)
        return self._money(total)

    def _parse_amount(self, raw: Any) -> Decimal:
        if not isinstance(raw, str):
            raw = str(raw)
        cleaned = raw.replace(",", "").replace(" ", "").strip()
        if cleaned.endswith("%"):
            cleaned = cleaned[:-1]
        try:
            value = Decimal(cleaned)
        except Exception as exc:
            raise SnapshotAdapterError(
                "invalid_amount",
                "Non-numeric amount value",
                {"value": raw},
            ) from exc
        if value < 0:
            raise SnapshotAdapterError(
                "invalid_amount",
                "Amount must not be negative",
                {"value": raw},
            )
        return self._money(value)

    @staticmethod
    def _money(value: Decimal | float) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
