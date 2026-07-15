"""Deterministic PDF rendering from persisted Report Content Representation."""

from __future__ import annotations

import hashlib
import io
from datetime import datetime
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.reports.constants import PDF_RENDERER_VERSION

_ARABIC_LABELS = {
    "cover": "الغلاف",
    "executive_summary": "الملخص التنفيذي",
    "waste_overview": "نظرة عامة على الهدر",
    "category_breakdown": "تفصيل الفئات",
    "recommendations": "التوصيات",
    "ai_insights": "رؤى الذكاء الاصطناعي",
    "scenario_provenance": "مصدر السيناريو",
    "forecast_and_delta": "التوقعات والفروقات",
    "provenance": "المصدر والتتبع",
}


def _section_title(key: str, *, report_language: str) -> str:
    if report_language.lower().startswith("ar"):
        return _ARABIC_LABELS.get(key, key.replace("_", " "))
    return key.replace("_", " ").title()


def _format_payload_lines(payload: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for key, value in sorted(payload.items()):
        if value is None:
            continue
        if isinstance(value, dict):
            lines.append(f"{key}:")
            lines.extend(f"  {sub}" for sub in _format_payload_lines(value))
        elif isinstance(value, list):
            lines.append(f"{key}: [{len(value)} items]")
        else:
            lines.append(f"{key}: {value}")
    return lines


def render_pdf(
    content: dict[str, Any],
    *,
    report_title: str,
    platform_name: str,
    report_language: str,
    include_cover_page: bool,
    include_provenance_appendix: bool,
) -> bytes:
    """Render a deterministic PDF from persisted content only."""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4, invariant=1)
    pdf.setTitle(report_title)
    pdf.setAuthor(platform_name)
    pdf.setSubject(f"Khazina Report {PDF_RENDERER_VERSION}")

    width, height = A4
    margin = 50
    y = height - margin

    if include_cover_page:
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(margin, y, report_title)
        y -= 30
        pdf.setFont("Helvetica", 12)
        pdf.drawString(margin, y, platform_name)
        y -= 20
        profile = str(content.get("profile", ""))
        pdf.drawString(margin, y, f"Profile: {profile}")
        y -= 20
        generated_at = str(content.get("generated_at", ""))
        pdf.drawString(margin, y, f"Generated: {generated_at}")
        pdf.showPage()
        y = height - margin

    sections = content.get("sections") or []
    pdf.setFont("Helvetica-Bold", 14)
    for section in sections:
        key = str(section.get("key", "section"))
        payload = dict(section.get("payload") or {})
        if key == "provenance" and not include_provenance_appendix:
            continue
        if y < margin + 80:
            pdf.showPage()
            y = height - margin
        pdf.drawString(margin, y, _section_title(key, report_language=report_language))
        y -= 22
        pdf.setFont("Helvetica", 10)
        for line in _format_payload_lines(payload):
            if y < margin + 20:
                pdf.showPage()
                y = height - margin
                pdf.setFont("Helvetica", 10)
            pdf.drawString(margin + 10, y, line[:110])
            y -= 14
        pdf.setFont("Helvetica-Bold", 14)
        y -= 8

    pdf.save()
    return buffer.getvalue()


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
