"""Scenario assumptions → typed engine input adapter."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from app.business.engines.scenario.input import ScenarioArchetype, ScenarioEngineInput
from app.decision.exceptions import SnapshotAdapterError
from app.scenario.constants import DEFAULT_HORIZON_QUARTERS


def _normalize_label(label: str) -> str:
    return label.strip().casefold()


REDUCTION_LABELS = frozenset(
    {
        "نسبة خفض الإنفاق",
        "reduction_percent",
        "spending_reduction",
        "reduction",
    }
)
SUPPLIERS_BEFORE_LABELS = frozenset(
    {"عدد الموردين قبل الدمج", "suppliers_before", "suppliers before"}
)
SUPPLIERS_AFTER_LABELS = frozenset(
    {"عدد الموردين بعد الدمج", "suppliers_after", "suppliers after"}
)
ADMIN_SAVINGS_LABELS = frozenset(
    {"توفير إداري متوقع", "admin_savings_rate", "admin_savings", "admin savings"}
)
REVENUE_GROWTH_LABELS = frozenset(
    {"نمو الإيرادات المتوقع", "revenue_growth_percent", "revenue_growth", "revenue growth"}
)
EXPANSION_COST_LABELS = frozenset({"تكلفة التوسع", "expansion_cost", "expansion cost"})
HORIZON_LABELS = frozenset({"الأفق الزمني", "horizon_quarters", "time_horizon", "horizon"})


def _assumption_field(item: Any, field: str) -> str:
    if isinstance(item, dict):
        return str(item.get(field, ""))
    return str(getattr(item, field, ""))


@dataclass(frozen=True, slots=True)
class _AssumptionIndex:
    by_normalized_label: dict[str, str]


class ScenarioAssumptionsAdapter:
    """Maps simulation assumption rows to ``ScenarioEngineInput`` parameters."""

    def adapt(
        self,
        assumptions: list[Any],
        *,
        scenario_name: str,
        scenario_description: str,
        baseline: Any,
    ) -> ScenarioEngineInput:
        if not assumptions:
            raise SnapshotAdapterError(
                "missing_assumptions",
                "At least one scenario assumption is required",
            )
        index = self._index_assumptions(assumptions)
        archetype = self._resolve_archetype(index, scenario_name, scenario_description)
        horizon = self._parse_horizon(index.by_normalized_label)

        if archetype == ScenarioArchetype.SPENDING_REDUCTION:
            reduction = self._require_percent(index, REDUCTION_LABELS, "reduction_percent")
            return ScenarioEngineInput(
                archetype=archetype,
                baseline=baseline,
                horizon_quarters=horizon,
                reduction_percent=reduction,
            )
        if archetype == ScenarioArchetype.SUPPLIER_CONSOLIDATION:
            return ScenarioEngineInput(
                archetype=archetype,
                baseline=baseline,
                horizon_quarters=horizon,
                suppliers_before=self._require_int(index, SUPPLIERS_BEFORE_LABELS),
                suppliers_after=self._require_int(index, SUPPLIERS_AFTER_LABELS),
                admin_savings_rate=self._require_percent(
                    index, ADMIN_SAVINGS_LABELS, "admin_savings_rate"
                ),
            )
        return ScenarioEngineInput(
            archetype=archetype,
            baseline=baseline,
            horizon_quarters=horizon,
            revenue_growth_percent=self._require_percent(
                index, REVENUE_GROWTH_LABELS, "revenue_growth_percent"
            ),
            expansion_cost=self._require_money(index, EXPANSION_COST_LABELS),
        )

    @staticmethod
    def _index_assumptions(assumptions: list[Any]) -> _AssumptionIndex:
        indexed: dict[str, str] = {}
        for item in assumptions:
            label = _assumption_field(item, "label").strip()
            value = _assumption_field(item, "value").strip()
            if not label or not value:
                raise SnapshotAdapterError(
                    "invalid_assumption",
                    "Each assumption requires a non-empty label and value",
                )
            normalized = _normalize_label(label)
            if normalized in indexed:
                raise SnapshotAdapterError(
                    "duplicate_assumption_label",
                    "Duplicate assumption label is not allowed",
                    {"label": label},
                )
            indexed[normalized] = value
        return _AssumptionIndex(by_normalized_label=indexed)

    def _resolve_archetype(
        self,
        index: _AssumptionIndex,
        scenario_name: str,
        scenario_description: str,
    ) -> ScenarioArchetype:
        scores = {
            ScenarioArchetype.SPENDING_REDUCTION: self._score_labels(
                index, REDUCTION_LABELS
            ),
            ScenarioArchetype.SUPPLIER_CONSOLIDATION: self._score_labels(
                index, SUPPLIERS_BEFORE_LABELS | SUPPLIERS_AFTER_LABELS
            ),
            ScenarioArchetype.MARKET_EXPANSION: self._score_labels(
                index, REVENUE_GROWTH_LABELS | EXPANSION_COST_LABELS
            ),
        }
        text = f"{scenario_name} {scenario_description}".casefold()
        if "تقليل" in text or "reduction" in text or "spending" in text:
            scores[ScenarioArchetype.SPENDING_REDUCTION] += 1
        if "دمج" in text or "supplier" in text:
            scores[ScenarioArchetype.SUPPLIER_CONSOLIDATION] += 1
        if "توسع" in text or "expansion" in text or "market" in text:
            scores[ScenarioArchetype.MARKET_EXPANSION] += 1

        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0].value))
        if ranked[0][1] == 0:
            raise SnapshotAdapterError(
                "ambiguous_archetype",
                "Unable to resolve scenario archetype from assumptions",
            )
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            raise SnapshotAdapterError(
                "ambiguous_archetype",
                "Multiple scenario archetypes match assumptions",
                {"candidates": [ranked[0][0].value, ranked[1][0].value]},
            )
        return ranked[0][0]

    @staticmethod
    def _score_labels(index: _AssumptionIndex, labels: frozenset[str]) -> int:
        return sum(
            1
            for label in labels
            if _normalize_label(label) in index.by_normalized_label
        )

    @staticmethod
    def _lookup(index: _AssumptionIndex, labels: frozenset[str]) -> str | None:
        for label in labels:
            value = index.by_normalized_label.get(_normalize_label(label))
            if value is not None:
                return value
        return None

    def _require_percent(
        self, index: _AssumptionIndex, labels: frozenset[str], field: str
    ) -> float:
        raw = self._lookup(index, labels)
        if raw is None:
            raise SnapshotAdapterError(
                "missing_required_assumption",
                f"Required assumption missing: {field}",
            )
        cleaned = raw.replace("%", "").replace("٪", "").strip()
        try:
            return float(Decimal(cleaned))
        except (InvalidOperation, ValueError) as exc:
            raise SnapshotAdapterError(
                "invalid_assumption_value",
                f"Assumption {field} must be numeric",
                {"value": raw},
            ) from exc

    def _require_int(self, index: _AssumptionIndex, labels: frozenset[str]) -> int:
        raw = self._lookup(index, labels)
        if raw is None:
            raise SnapshotAdapterError(
                "missing_required_assumption",
                "Required supplier count assumption missing",
            )
        try:
            return int(Decimal(re.sub(r"[^\d.]", "", raw)))
        except (InvalidOperation, ValueError) as exc:
            raise SnapshotAdapterError(
                "invalid_assumption_value",
                "Supplier count assumption must be an integer",
                {"value": raw},
            ) from exc

    def _require_money(self, index: _AssumptionIndex, labels: frozenset[str]) -> float:
        raw = self._lookup(index, labels)
        if raw is None:
            raise SnapshotAdapterError(
                "missing_required_assumption",
                "Required expansion_cost assumption missing",
            )
        cleaned = raw.upper().replace("ر.س", "").replace("SAR", "").strip()
        multiplier = 1.0
        if cleaned.endswith("M"):
            multiplier = 1_000_000.0
            cleaned = cleaned[:-1]
        elif cleaned.endswith("K"):
            multiplier = 1_000.0
            cleaned = cleaned[:-1]
        cleaned = cleaned.replace(",", "").strip()
        try:
            return float(Decimal(cleaned) * Decimal(str(multiplier)))
        except (InvalidOperation, ValueError) as exc:
            raise SnapshotAdapterError(
                "invalid_assumption_value",
                "expansion_cost must be a monetary value",
                {"value": raw},
            ) from exc

    @staticmethod
    def _parse_horizon(indexed: dict[str, str]) -> int:
        raw = None
        for label in HORIZON_LABELS:
            raw = indexed.get(_normalize_label(label))
            if raw is not None:
                break
        if raw is None:
            return DEFAULT_HORIZON_QUARTERS
        match = re.search(r"\d+", raw)
        if not match:
            return DEFAULT_HORIZON_QUARTERS
        return int(match.group(0))
