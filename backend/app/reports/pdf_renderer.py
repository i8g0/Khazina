"""Deterministic PDF rendering from persisted Report Content Representation."""

from __future__ import annotations

import hashlib
import io
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from app.reports.constants import PDF_RENDERER_VERSION
from app.presentation.executive_sanitize import sanitize_executive_text

_FONT_REGISTERED = False
_FONT_REGULAR = "NotoNaskhArabic"
_FONT_BOLD = "NotoNaskhArabic-Bold"

_ASSETS_DIR = Path(__file__).resolve().parent / "assets"

_ARABIC_LABELS = {
    "cover": "الغلاف",
    "executive_summary": "الملخص التنفيذي",
    "risk_summary": "ملخص المخاطر",
    "top_risks": "أبرز المخاطر",
    "mitigation_status": "حالة التخفيف",
    "register_statistics": "إحصائيات السجل",
    "waste_overview": "نظرة عامة على الهدر",
    "waste_analysis": "تحليل الهدر",
    "category_breakdown": "تفصيل الفئات",
    "category_breakdowns": "تفصيل الفئات",
    "vendor_findings": "نتائج الموردين",
    "risk_explanation": "شرح المخاطر",
    "recommendations": "التوصيات",
    "ai_insights": "رؤى الذكاء الاصطناعي",
    "scenario_overview": "نظرة عامة على السيناريو",
    "scenario_provenance": "مصدر السيناريو",
    "forecast_and_delta": "التوقعات والفروقات",
    "impact_and_actions": "الأثر والإجراءات",
    "baseline_context": "سياق خط الأساس",
    "key_metrics": "المؤشرات الرئيسية",
    "current_situation": "الوضع الحالي",
    "financial_impact": "الأثر المالي",
    "operational_impact": "الأثر التشغيلي",
    "evidence": "الأدلة",
    "proposed_decisions": "القرارات المقترحة",
    "next_steps": "الخطوات التالية",
    "text": "النص",
    "items": "البنود",
    "title": "العنوان",
    "description": "الوصف",
    "priority": "الأولوية",
    "amount": "المبلغ",
    "percentage": "النسبة",
    "category_name": "الفئة",
    "vendor_name": "المورد",
    "name": "الاسم",
    "score": "الدرجة",
    "status": "الحالة",
    "organization_name": "المؤسسة",
    "period_label": "الفترة",
    "run_title": "عنوان التحليل",
    "source_file_name": "ملف المصدر",
    "completed_at": "تاريخ الإكمال",
    "generated_at": "تاريخ التوليد",
    "profile": "الملف",
}

# Executive-only section titles (board-ready naming)
_EXECUTIVE_SECTION_TITLES: dict[str, str] = {
    "executive_summary": "الملخص التنفيذي",
    "key_metrics": "أبرز المؤشرات المالية",
    "waste_analysis": "تحليل الهدر",
    "risk_summary": "تحليل المخاطر",
    "risk_explanation": "تحليل المخاطر",
    "top_risks": "أبرز المخاطر",
    "mitigation_status": "حالة التخفيف",
    "current_situation": "الوضع الحالي",
    "financial_impact": "الأثر المالي",
    "operational_impact": "الأثر التشغيلي",
    "evidence": "الأدلة",
    "proposed_decisions": "القرارات المقترحة",
    "next_steps": "الخطوات التالية",
    "recommendations": "التوصيات التنفيذية",
    "scenario_overview": "تحليل السيناريو",
    "forecast_and_delta": "تحليل السيناريو — التوقعات",
    "impact_and_actions": "الأثر المالي والإجراءات ذات الأولوية",
    "ai_insights": "رؤى تنفيذية",
}

# Sections never shown in executive PDF
_TECHNICAL_SECTIONS = frozenset(
    {
        "cover",
        "provenance",
        "scenario_provenance",
        "baseline_context",
    }
)

# Payload keys hidden from executives
_FORBIDDEN_PAYLOAD_KEYS = frozenset(
    {
        "facts",
        "source",
        "profile",
        "facts_contract_version",
        "engine_id",
        "engine_version",
        "tasks_executed",
        "source_snapshot_id",
        "metadata",
        "ai_metadata",
        "source_context",
        "traceability",
        "scenario_id",
        "department_id",
        "source_file_id",
        "report_language",
        "date_display_format",
        "currency_display_code",
        "parsed_format",
        "prompt_version",
        "model",
        "item_index",
        "deterministic_source",
        "ai_insights_consumed",
        "top_category_code",
        "archetype",
        "assumptions_count",
    }
)

_HEADLINE_LABELS: dict[str, str] = {
    "total_waste_amount": "إجمالي الهدر المالي",
    "waste_percentage": "نسبة الهدر",
    "potential_savings_amount": "الوفورات المحتملة",
    "active_savings_opportunities": "فرص التوفير النشطة",
}

_LIST_ITEM_KEYS = frozenset(
    {
        "items",
        "category_breakdowns",
        "vendor_findings",
        "plans",
        "facts",
        "assumptions",
        "chart_points",
        "comparison_metrics",
        "impact_items",
        "action_items",
    }
)


def _register_fonts() -> None:
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return
    regular = _ASSETS_DIR / "NotoNaskhArabic-Regular.ttf"
    if not regular.is_file():
        raise FileNotFoundError(f"Arabic PDF font not found: {regular}")
    pdfmetrics.registerFont(TTFont(_FONT_REGULAR, str(regular)))
    pdfmetrics.registerFont(TTFont(_FONT_BOLD, str(regular)))
    _FONT_REGISTERED = True


def _is_arabic(report_language: str) -> bool:
    return report_language.lower().startswith("ar")


def _prepare_text(text: str, *, report_language: str) -> str:
    raw = str(text).replace("\n", " ").strip()
    if not raw:
        return ""
    if not _is_arabic(report_language):
        return raw
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        reshaped = arabic_reshaper.reshape(raw)
        return get_display(reshaped)
    except Exception:
        return raw


def _section_title(key: str, *, report_language: str) -> str:
    if _is_arabic(report_language):
        return _EXECUTIVE_SECTION_TITLES.get(
            key, _ARABIC_LABELS.get(key, key.replace("_", " "))
        )
    return key.replace("_", " ").title()


def _prepare_executive_section_payload(key: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Transform persisted section payload into executive-safe presentation."""
    if key == "key_metrics":
        headline = payload.get("headline")
        if isinstance(headline, dict) and headline:
            return {
                _HEADLINE_LABELS.get(k, k): v for k, v in headline.items()
            }
        return {}
    cleaned: dict[str, Any] = {}
    for field, value in payload.items():
        if field in _FORBIDDEN_PAYLOAD_KEYS:
            continue
        if field == "text" and isinstance(value, str):
            cleaned[field] = sanitize_executive_text(value)
            continue
        if field == "items" and isinstance(value, list):
            cleaned[field] = [
                {
                    k: sanitize_executive_text(str(v)) if k in {"title", "description"} and isinstance(v, str) else v
                    for k, v in item.items()
                    if k not in _FORBIDDEN_PAYLOAD_KEYS
                }
                for item in value
                if isinstance(item, dict)
            ]
            continue
        cleaned[field] = value
    return cleaned


def _label(key: str, *, report_language: str) -> str:
    if _is_arabic(report_language):
        return _ARABIC_LABELS.get(key, key.replace("_", " "))
    return key.replace("_", " ")


def _format_scalar(key: str, value: Any, *, report_language: str) -> str:
    label = _label(key, report_language=report_language)
    return f"{label}: {value}"


def _format_list_item(item: Any, *, indent: int, report_language: str) -> list[str]:
    prefix = "  " * indent
    if isinstance(item, dict):
        lines: list[str] = []
        title = item.get("title") or item.get("name") or item.get("category_name")
        if title:
            lines.append(f"{prefix}• {_prepare_text(str(title), report_language=report_language)}")
        for key, value in item.items():
            if key in {"title", "name", "category_name"}:
                continue
            if key in _FORBIDDEN_PAYLOAD_KEYS:
                continue
            if value is None:
                continue
            if isinstance(value, (dict, list)):
                lines.extend(
                    _format_payload_lines(
                        {str(key): value},
                        indent=indent + 1,
                        report_language=report_language,
                    )
                )
            else:
                lines.append(
                    prefix
                    + "  "
                    + _prepare_text(
                        _format_scalar(str(key), value, report_language=report_language),
                        report_language=report_language,
                    )
                )
        return lines
    return [f"{prefix}• {_prepare_text(str(item), report_language=report_language)}"]


def _format_payload_lines(
    payload: dict[str, Any],
    *,
    indent: int = 0,
    report_language: str,
) -> list[str]:
    lines: list[str] = []
    prefix = "  " * indent
    for key, value in sorted(payload.items()):
        if value is None:
            continue
        if key in _FORBIDDEN_PAYLOAD_KEYS:
            continue
        if key == "text" and isinstance(value, str):
            for chunk in textwrap.wrap(value, width=90):
                lines.append(
                    prefix + _prepare_text(chunk, report_language=report_language)
                )
            continue
        if isinstance(value, dict):
            lines.append(
                prefix + _prepare_text(_label(str(key), report_language=report_language) + ":", report_language=report_language)
            )
            lines.extend(
                _format_payload_lines(value, indent=indent + 1, report_language=report_language)
            )
        elif isinstance(value, list):
            if not value:
                continue
            if key in _LIST_ITEM_KEYS or (
                value and isinstance(value[0], dict)
            ):
                label = _label(str(key), report_language=report_language)
                lines.append(
                    prefix
                    + _prepare_text(
                        f"{label}:",
                        report_language=report_language,
                    )
                )
                for item in value[:25]:
                    lines.extend(
                        _format_list_item(item, indent=indent + 1, report_language=report_language)
                    )
                if len(value) > 25:
                    lines.append(
                        prefix
                        + _prepare_text(
                            f"... +{len(value) - 25} أخرى",
                            report_language=report_language,
                        )
                    )
            else:
                lines.append(
                    prefix
                    + _prepare_text(
                        _format_scalar(str(key), ", ".join(str(v) for v in value), report_language=report_language),
                        report_language=report_language,
                    )
                )
        else:
            lines.append(
                prefix
                + _prepare_text(
                    _format_scalar(str(key), value, report_language=report_language),
                    report_language=report_language,
                )
            )
    return lines


def _draw_line(
    pdf: canvas.Canvas,
    text: str,
    *,
    y: float,
    margin: float,
    width: float,
    font_name: str,
    font_size: int,
    report_language: str,
) -> float:
    pdf.setFont(font_name, font_size)
    prepared = _prepare_text(text, report_language=report_language)
    max_width = width - (2 * margin)
    if _is_arabic(report_language):
        pdf.drawRightString(width - margin, y, prepared[:200])
    else:
        pdf.drawString(margin, y, prepared[:200])
    return y - (font_size + 4)


def render_pdf(
    content: dict[str, Any],
    *,
    report_title: str,
    platform_name: str,
    report_language: str,
    include_cover_page: bool,
    include_provenance_appendix: bool,
) -> bytes:
    """Render board-ready executive PDF from persisted content."""
    del include_provenance_appendix  # never shown in executive layout
    from app.reports.executive_pdf_layout import render_executive_pdf

    return render_executive_pdf(
        content,
        report_title=report_title,
        platform_name=platform_name,
        report_language=report_language,
        include_cover_page=include_cover_page,
    )


def export_fingerprint(pdf_bytes: bytes) -> str:
    return hashlib.sha256(pdf_bytes).hexdigest()


def preferences_fingerprint(
    *,
    report_language: str,
    include_cover_page: bool,
    include_provenance_appendix: bool,
) -> str:
    payload = (
        f"{PDF_RENDERER_VERSION}|{report_language}|"
        f"{include_cover_page}|{include_provenance_appendix}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
