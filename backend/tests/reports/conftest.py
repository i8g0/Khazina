"""Shared fixtures for report builder tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

from app.business.engines.waste.engine import WasteEngine
from app.business.engines.waste.input import WasteCategoryInput, WasteEngineInput
from app.business.facts.contract import FactsContract
from app.db.models.enums import AnalysisRunStatus, AnalysisType


def sample_waste_engine_input() -> WasteEngineInput:
    return WasteEngineInput(
        total_spend=50_000_000.0,
        total_waste_amount=2_340_000.0,
        categories=(
            WasteCategoryInput("overlapping_contracts", 745_000.0),
            WasteCategoryInput("operations", 520_000.0),
            WasteCategoryInput("finance", 1_075_000.0),
        ),
        organization_id="org-123",
        period="2026-Q2",
        generated_at=datetime(2026, 7, 15, tzinfo=UTC),
    )


def sample_waste_facts() -> FactsContract:
    return WasteEngine().run(sample_waste_engine_input())


def sample_scenario_facts() -> FactsContract:
    return FactsContract(
        contract_version="1.0",
        engine_id="scenario",
        engine_version="1.0.0",
        generated_at=datetime(2026, 7, 15, tzinfo=UTC),
        facts=(),
    )


def sample_ai_insights() -> dict[str, Any]:
    return {
        "generated_at": "2026-07-15T10:00:00+00:00",
        "prompt_version": "1.0",
        "model": "qwen3.5:2b",
        "executive_summary": "ملخص تنفيذي للإدارة حول الهدر المالي.",
        "risk_explanation": "تحليل المخاطر: مستوى الهدر مرتفع.",
        "narrative": {},
    }


def mock_waste_run(
    org_id: uuid.UUID,
    run_id: uuid.UUID,
    *,
    with_ai: bool = True,
) -> MagicMock:
    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.analysis_type = AnalysisType.FINANCIAL_WASTE
    run.status = AnalysisRunStatus.COMPLETED
    run.title = "Waste Analysis Q2"
    run.source_file_id = uuid.UUID("33333333-3333-3333-3333-333333333333")
    run.reporting_period_id = uuid.UUID("44444444-4444-4444-4444-444444444444")
    run.source_snapshot_id = uuid.UUID("55555555-5555-5555-5555-555555555555")
    run.completed_at = datetime(2026, 7, 15, tzinfo=UTC)
    metadata: dict[str, Any] = {"facts_contract": sample_waste_facts().to_dict()}
    if with_ai:
        metadata["ai_insights"] = sample_ai_insights()
    run.runtime_metadata = metadata
    return run


def mock_waste_result(run_id: uuid.UUID) -> MagicMock:
    result = MagicMock()
    result.id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    result.analysis_run_id = run_id
    result.total_waste_amount = Decimal("2340000.00")
    result.waste_percentage = Decimal("4.68")
    result.top_category_name = "finance"
    result.potential_savings_amount = Decimal("500000.00")
    result.active_savings_opportunities = 3
    return result


def mock_breakdown(run_id: uuid.UUID) -> MagicMock:
    row = MagicMock()
    row.id = uuid.UUID("22222222-2222-2222-2222-222222222222")
    row.analysis_run_id = run_id
    row.category_name = "finance"
    row.amount = Decimal("1075000.00")
    row.percentage = Decimal("45.94")
    row.department_id = uuid.UUID("66666666-6666-6666-6666-666666666666")
    return row
