"""Shared fixtures for scenario tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.business.engines.scenario.input import (
    ScenarioArchetype,
    ScenarioBaselineInput,
    ScenarioCategoryBaseline,
    ScenarioEngineInput,
)


def sample_scenario_snapshot_payload() -> dict:
    return {
        "source_file_name": "Budget_Q2.xlsx",
        "sheets": [
            {
                "name": "Departments",
                "columns": ["department", "amount", "total_spend"],
                "rows": [
                    {
                        "row_number": 2,
                        "values": {
                            "department": "procurement",
                            "amount": "18200000",
                            "total_spend": "48750000",
                        },
                    },
                    {
                        "row_number": 3,
                        "values": {
                            "department": "operations",
                            "amount": "15300000",
                            "total_spend": "48750000",
                        },
                    },
                    {
                        "row_number": 4,
                        "values": {
                            "department": "finance",
                            "amount": "15250000",
                            "total_spend": "48750000",
                        },
                    },
                ],
            }
        ],
    }


def sample_spending_reduction_assumptions() -> list[dict[str, str]]:
    return [
        {"label": "نسبة خفض الإنفاق", "value": "10%"},
        {"label": "نطاق التطبيق", "value": "جميع الأقسام"},
        {"label": "الأفق الزمني", "value": "3 أرباع"},
    ]


def sample_baseline_input() -> ScenarioBaselineInput:
    return ScenarioBaselineInput(
        total_baseline=48_750_000.0,
        categories=(
            ScenarioCategoryBaseline("finance", 15_250_000.0),
            ScenarioCategoryBaseline("operations", 15_300_000.0),
            ScenarioCategoryBaseline("procurement", 18_200_000.0),
        ),
        organization_id="org-123",
        period="2026-Q2",
        generated_at=datetime(2026, 7, 15, tzinfo=UTC),
    )


def sample_spending_reduction_input() -> ScenarioEngineInput:
    return ScenarioEngineInput(
        archetype=ScenarioArchetype.SPENDING_REDUCTION,
        baseline=sample_baseline_input(),
        reduction_percent=10.0,
        horizon_quarters=3,
    )
