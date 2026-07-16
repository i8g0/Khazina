"""Sprint 7.1 — risk context for simulation."""

from __future__ import annotations

import uuid

from app.scenario.risk_context import SimulationRiskContext


def test_simulation_risk_context_prompt_block_arabic() -> None:
    ctx = SimulationRiskContext(
        analysis_run_id=str(uuid.uuid4()),
        posture_ar="مرتفع",
        total_findings=5,
        high_priority_count=2,
        narrative_summary="إدارة المشتريات تمثل 34% من إجمالي الهدر.",
        top_risks=(
            {
                "title": "تركّز على موردين",
                "exposure": "2.3 مليون ر.س",
                "priority": "عالية",
            },
        ),
        recommendations=("تنويع قاعدة الموردين",),
        departments_exposed=("إدارة المشتريات",),
        suppliers_exposed=("مورد أ",),
    )
    block = ctx.to_prompt_block()
    assert "سياق المخاطر" in block
    assert "مرتفع" in block
    assert "تركّز على موردين" in block
    assert "Risk" not in block
    assert "exposure" not in block.lower()
