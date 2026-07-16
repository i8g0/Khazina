"""Risk v1 Snapshot-to-Engine Input Adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from app.business.engines.risk.input import (
    DepartmentWasteMetric,
    FinancialMetricsInput,
    RiskEngineInput,
    SimulationSummaryReference,
    SupplierWasteMetric,
    WasteCategoryMetric,
    WasteFactsReference,
)
from app.decision.adapters.waste_v1 import WasteSnapshotAdapterV1, _match_columns
from app.decision.constants import (
    ACTUAL_SUM_ALIASES,
    BUDGET_SUM_ALIASES,
    DEPARTMENT_ALIASES,
    SOURCE_DATASET_FINANCIAL_SNAPSHOT_V1,
    SUPPLIER_ALIASES,
)


def _money(value: Decimal | float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class RiskSnapshotAdapterV1:
    """Maps Financial Snapshot schema v1 payload to ``RiskEngineInput``."""

    def __init__(self, *, waste_adapter: WasteSnapshotAdapterV1 | None = None) -> None:
        self._waste_adapter = waste_adapter or WasteSnapshotAdapterV1()

    def adapt(
        self,
        payload: dict[str, Any],
        *,
        organization_id: str,
        snapshot_id: str,
        period: str,
        generated_at: datetime | None = None,
        waste_facts: WasteFactsReference | None = None,
        simulation_summary: SimulationSummaryReference | None = None,
        existing_register_summary: dict[str, int] | None = None,
    ) -> RiskEngineInput:
        waste_input = self._waste_adapter.adapt(
            payload,
            organization_id=organization_id,
            period=period,
            generated_at=generated_at,
        )

        total_spend = _money(waste_input.total_spend)
        total_waste = _money(waste_input.total_waste_amount)
        waste_pct = _money((total_waste / total_spend) * Decimal("100"))

        categories: list[WasteCategoryMetric] = []
        for category in waste_input.categories:
            amount = _money(category.amount)
            share = (
                _money((amount / total_waste) * Decimal("100"))
                if total_waste > 0
                else Decimal("0.00")
            )
            categories.append(
                WasteCategoryMetric(
                    category_name=category.category_name,
                    amount=amount,
                    share_of_waste=share,
                )
            )

        budget_total, actual_total = self._extract_budget_actual(payload)
        departments, suppliers = self._aggregate_dimensions(payload, total_waste)
        risk_metrics = payload.get("risk_metrics") if isinstance(payload, dict) else None
        current_assets = None
        current_liabilities = None
        if isinstance(risk_metrics, dict):
            current_assets = self._optional_decimal(risk_metrics.get("current_assets"))
            current_liabilities = self._optional_decimal(
                risk_metrics.get("current_liabilities")
            )

        timestamp = generated_at or waste_input.generated_at or datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        return RiskEngineInput(
            organization_id=organization_id,
            snapshot_id=snapshot_id,
            reporting_period=period or "unknown",
            financial_metrics=FinancialMetricsInput(
                total_spend=total_spend,
                total_waste_amount=total_waste,
                waste_percentage=waste_pct,
                budget_total=budget_total,
                actual_total=actual_total,
                current_assets=current_assets,
                current_liabilities=current_liabilities,
                categories=tuple(categories),
                departments=tuple(departments),
                suppliers=tuple(suppliers),
            ),
            waste_facts=waste_facts,
            simulation_summary=simulation_summary,
            existing_register_summary=existing_register_summary,
            source_dataset=SOURCE_DATASET_FINANCIAL_SNAPSHOT_V1,
            generated_at=timestamp,
        )

    def _extract_budget_actual(
        self, payload: dict[str, Any]
    ) -> tuple[Decimal | None, Decimal | None]:
        sheets = payload.get("sheets")
        if not isinstance(sheets, list):
            return None, None
        for sheet in sheets:
            if not isinstance(sheet, dict):
                continue
            columns = tuple(sheet.get("columns") or [])
            budget_cols = _match_columns(columns, BUDGET_SUM_ALIASES)
            actual_cols = _match_columns(columns, ACTUAL_SUM_ALIASES)
            if not budget_cols or not actual_cols:
                continue
            budget_col = budget_cols[0]
            actual_col = actual_cols[0]
            budget_sum = Decimal("0.00")
            actual_sum = Decimal("0.00")
            found = False
            for row in sheet.get("rows") or []:
                if not isinstance(row, dict):
                    continue
                values = row.get("values") or {}
                if budget_col in values and values[budget_col] not in (None, ""):
                    budget_sum += self._parse_decimal(values[budget_col])
                    found = True
                if actual_col in values and values[actual_col] not in (None, ""):
                    actual_sum += self._parse_decimal(values[actual_col])
                    found = True
            if found:
                return _money(budget_sum), _money(actual_sum)
        return None, None

    def _aggregate_dimensions(
        self, payload: dict[str, Any], total_waste: Decimal
    ) -> tuple[list[DepartmentWasteMetric], list[SupplierWasteMetric]]:
        sheets = payload.get("sheets")
        if not isinstance(sheets, list) or total_waste <= 0:
            return [], []
        dept_totals: dict[str, Decimal] = {}
        supplier_totals: dict[str, Decimal] = {}
        for sheet in sheets:
            if not isinstance(sheet, dict):
                continue
            columns = tuple(sheet.get("columns") or [])
            dept_cols = _match_columns(columns, DEPARTMENT_ALIASES)
            supplier_cols = _match_columns(columns, SUPPLIER_ALIASES)
            amount_cols = _match_columns(
                columns,
                frozenset({"amount", "waste", "waste_amount", "cost", "مبلغ", "الهدر"}),
            )
            if not amount_cols:
                continue
            amount_col = amount_cols[0]
            for row in sheet.get("rows") or []:
                if not isinstance(row, dict):
                    continue
                values = row.get("values") or {}
                amount_raw = values.get(amount_col)
                if amount_raw in (None, ""):
                    continue
                amount = self._parse_decimal(amount_raw)
                if amount <= 0:
                    continue
                if dept_cols:
                    dept = str(values.get(dept_cols[0], "")).strip()
                    if dept:
                        dept_totals[dept] = dept_totals.get(dept, Decimal("0")) + amount
                if supplier_cols:
                    supplier = str(values.get(supplier_cols[0], "")).strip()
                    if supplier:
                        supplier_totals[supplier] = (
                            supplier_totals.get(supplier, Decimal("0")) + amount
                        )
        departments = [
            DepartmentWasteMetric(
                department_name=name,
                amount=_money(amount),
                share_of_waste=_money((amount / total_waste) * Decimal("100")),
            )
            for name, amount in sorted(dept_totals.items(), key=lambda x: x[1], reverse=True)
        ]
        suppliers = [
            SupplierWasteMetric(
                supplier_name=name,
                amount=_money(amount),
                share_of_waste=_money((amount / total_waste) * Decimal("100")),
            )
            for name, amount in sorted(supplier_totals.items(), key=lambda x: x[1], reverse=True)
        ]
        return departments, suppliers

    @staticmethod
    def _optional_decimal(raw: Any) -> Decimal | None:
        if raw is None or raw == "":
            return None
        return _money(Decimal(str(raw).replace(",", "").strip()))

    @staticmethod
    def _parse_decimal(raw: Any) -> Decimal:
        cleaned = str(raw).replace(",", "").replace(" ", "").strip()
        if cleaned.endswith("%"):
            cleaned = cleaned[:-1]
        return _money(Decimal(cleaned))
