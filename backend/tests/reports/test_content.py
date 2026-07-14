"""Report Content Representation serialization tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.reports.content import (
    ExtendedMetadata,
    ReportContentRepresentation,
    ReportSection,
    build_extended_metadata,
    canonical_serialize,
    content_fingerprint,
)


def test_canonical_serialize_is_deterministic() -> None:
    content = ReportContentRepresentation(
        report_document_version="1.0",
        profile="waste_decision",
        generated_at=datetime(2026, 7, 15, 12, 0, tzinfo=UTC),
        source_analysis_run_id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        organization_id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        report_id=uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        sections=(
            ReportSection(key="cover", payload={"run_title": "Test"}),
            ReportSection(key="executive_summary", payload={"text": "Summary"}),
        ),
        extended_metadata=build_extended_metadata(
            input_fingerprint="abc123",
            sections_included=("cover", "executive_summary"),
            ai_insights_consumed=False,
            ai_insights_generated_at=None,
            baseline_run_id=None,
        ),
    )
    first = canonical_serialize(content)
    second = canonical_serialize(content)
    assert first == second
    assert content_fingerprint(content) == content_fingerprint(first)


def test_round_trip_from_dict() -> None:
    original = ReportContentRepresentation(
        report_document_version="1.0",
        profile="scenario",
        generated_at=datetime(2026, 7, 15, tzinfo=UTC),
        source_analysis_run_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        report_id=uuid.uuid4(),
        sections=(ReportSection(key="cover", payload={"x": 1}),),
        extended_metadata=ExtendedMetadata(
            builder_version="1.0.0",
            input_fingerprint="fp",
            sections_included=("cover",),
            ai_insights_consumed=False,
            ai_insights_generated_at=None,
            baseline_run_id=None,
        ),
    )
    restored = ReportContentRepresentation.from_dict(original.to_dict())
    assert canonical_serialize(restored) == canonical_serialize(original)
