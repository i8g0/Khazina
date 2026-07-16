"""Section assembler tests."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

from app.reports.loaders import OrganizationContext, WasteReportInputs
from app.reports.sections import assemble_waste_sections, build_waste_executive_summary
from tests.reports.conftest import (
    mock_breakdown,
    mock_waste_result,
    mock_waste_run,
    sample_waste_facts,
)


def test_waste_executive_summary_uses_ai_when_present() -> None:
    org_id = uuid.uuid4()
    run_id = uuid.uuid4()
    run = mock_waste_run(org_id, run_id, with_ai=True)
    inputs = WasteReportInputs(
        run=run,
        facts=sample_waste_facts(),
        waste_result=mock_waste_result(run_id),
        category_breakdowns=(mock_breakdown(run_id),),
        vendor_findings=(),
        recommendations=(),
        ai_insights=run.runtime_metadata["ai_insights"],
        context=OrganizationContext(org_id, "Org", "2026-Q2", "file.xlsx"),
    )
    section = build_waste_executive_summary(inputs)
    assert section.payload["source"] == "ai_insights"
    assert "ملخص تنفيذي" in section.payload["text"]


def test_waste_executive_summary_fallback_without_ai() -> None:
    org_id = uuid.uuid4()
    run_id = uuid.uuid4()
    run = mock_waste_run(org_id, run_id, with_ai=False)
    inputs = WasteReportInputs(
        run=run,
        facts=sample_waste_facts(),
        waste_result=mock_waste_result(run_id),
        category_breakdowns=(),
        vendor_findings=(),
        recommendations=(),
        ai_insights=None,
        context=OrganizationContext(org_id, "Org", None, None),
    )
    section = build_waste_executive_summary(inputs)
    assert section.payload["source"] == "facts_gold_fallback"
    assert "4.68" in section.payload["text"]


def test_assemble_waste_sections_includes_required_keys() -> None:
    org_id = uuid.uuid4()
    run_id = uuid.uuid4()
    run = mock_waste_run(org_id, run_id, with_ai=True)
    rec = MagicMock()
    rec.title = "Rec"
    rec.description = "Desc"
    rec.priority = "high"
    rec.confidence_label = None
    rec.estimated_savings_amount = Decimal("1000")
    rec.source_context = {}
    inputs = WasteReportInputs(
        run=run,
        facts=sample_waste_facts(),
        waste_result=mock_waste_result(run_id),
        category_breakdowns=(mock_breakdown(run_id),),
        vendor_findings=(),
        recommendations=(rec,),
        ai_insights=run.runtime_metadata["ai_insights"],
        context=OrganizationContext(org_id, "Org", "2026-Q2", "file.xlsx"),
    )
    sections = assemble_waste_sections(inputs)
    keys = {section.key for section in sections}
    assert keys >= {
        "cover",
        "executive_summary",
        "decision_highlights",
        "key_metrics",
        "waste_analysis",
        "risk_explanation",
        "recommendations",
        "provenance",
    }
