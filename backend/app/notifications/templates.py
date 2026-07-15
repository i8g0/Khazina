"""Deterministic notification title/body templates — no LLM."""

from __future__ import annotations

from typing import Any


def analysis_completed_message(*, run_title: str, period_label: str | None) -> tuple[str, str]:
    period = period_label or "—"
    title = f"اكتمل التحليل: {run_title}"
    body = f"اكتمل تحليل الهدر المالي «{run_title}» للفترة {period}."
    return title, body


def scenario_completed_message(
    *,
    run_title: str,
    scenario_name: str | None,
    archetype: str | None,
    period_label: str | None,
) -> tuple[str, str]:
    period = period_label or "—"
    scenario = scenario_name or run_title
    archetype_text = f" ({archetype})" if archetype else ""
    title = f"اكتملت المحاكاة: {scenario}"
    body = (
        f"اكتملت محاكاة السيناريو «{scenario}»{archetype_text} "
        f"للفترة {period}."
    )
    return title, body


def ai_recommendations_completed_message(
    *,
    run_title: str,
    recommendation_count: int,
) -> tuple[str, str]:
    title = f"توصيات الذكاء الاصطناعي جاهزة: {run_title}"
    body = (
        f"تم إنشاء {recommendation_count} توصية للتحليل «{run_title}»."
    )
    return title, body


def report_generated_message(*, report_title: str, report_type: str) -> tuple[str, str]:
    title = f"تم إنشاء التقرير: {report_title}"
    body = f"التقرير «{report_title}» ({report_type}) جاهز كمسودة."
    return title, body


def report_published_message(*, report_title: str, report_type: str) -> tuple[str, str]:
    title = f"تم نشر التقرير: {report_title}"
    body = f"التقرير «{report_title}» ({report_type}) منشور وجاهز للمراجعة."
    return title, body


def analysis_failed_message(
    *,
    run_title: str,
    error_code: str | None,
) -> tuple[str, str]:
    code = error_code or "unknown"
    title = f"فشل التحليل: {run_title}"
    body = f"تعذّر إكمال تحليل الهدر المالي «{run_title}» (رمز الخطأ: {code})."
    return title, body


def scenario_failed_message(
    *,
    run_title: str,
    error_code: str | None,
) -> tuple[str, str]:
    code = error_code or "unknown"
    title = f"فشلت المحاكاة: {run_title}"
    body = f"تعذّر إكمال محاكاة السيناريو «{run_title}» (رمز الخطأ: {code})."
    return title, body


def build_payload_representation(
    *,
    platform_event_kind: str,
    title: str,
    body: str,
    source_entity_type: str,
    source_entity_id: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "notification_version": "1.0",
        "platform_event_kind": platform_event_kind,
        "title": title,
        "body": body,
        "source_entity_type": source_entity_type,
        "source_entity_id": source_entity_id,
        "metadata": metadata,
    }
