"""Deterministic template tests."""

from __future__ import annotations

from app.notifications.templates import (
    ai_recommendations_completed_message,
    analysis_completed_message,
    build_payload_representation,
    report_generated_message,
    report_published_message,
    scenario_completed_message,
)


def test_analysis_completed_message_is_deterministic() -> None:
    first = analysis_completed_message(run_title="Waste Q2", period_label="2026-Q2")
    second = analysis_completed_message(run_title="Waste Q2", period_label="2026-Q2")
    assert first == second
    assert "Waste Q2" in first[0]


def test_scenario_completed_message_is_deterministic() -> None:
    first = scenario_completed_message(
        run_title="Sim",
        scenario_name="Cost Cut",
        archetype="cost_reduction",
        period_label="2026-Q2",
    )
    second = scenario_completed_message(
        run_title="Sim",
        scenario_name="Cost Cut",
        archetype="cost_reduction",
        period_label="2026-Q2",
    )
    assert first == second


def test_ai_recommendations_message_is_deterministic() -> None:
    first = ai_recommendations_completed_message(
        run_title="Waste Q2", recommendation_count=3
    )
    second = ai_recommendations_completed_message(
        run_title="Waste Q2", recommendation_count=3
    )
    assert first == second


def test_report_messages_are_deterministic() -> None:
    generated = report_generated_message(
        report_title="Report A", report_type="analysis"
    )
    published = report_published_message(
        report_title="Report A", report_type="analysis"
    )
    assert generated == report_generated_message(
        report_title="Report A", report_type="analysis"
    )
    assert published == report_published_message(
        report_title="Report A", report_type="analysis"
    )


def test_payload_representation_is_stable() -> None:
    payload = build_payload_representation(
        platform_event_kind="analysis_completed",
        title="t",
        body="b",
        source_entity_type="analysis_run",
        source_entity_id="11111111-1111-1111-1111-111111111111",
        metadata={"analysis_type": "financial_waste"},
    )
    again = build_payload_representation(
        platform_event_kind="analysis_completed",
        title="t",
        body="b",
        source_entity_type="analysis_run",
        source_entity_id="11111111-1111-1111-1111-111111111111",
        metadata={"analysis_type": "financial_waste"},
    )
    assert payload == again
