"""Enterprise consulting-style PDF layout (Deloitte / McKinsey class)."""

from __future__ import annotations

import textwrap
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from app.presentation.business_labels import category_label_ar
from app.presentation.executive_recommendation import (
    ExecutiveRecommendationFields,
    parse_executive_recommendation,
)
from app.presentation.executive_sanitize import sanitize_executive_text

_FONT_REGISTERED = False
_FONT_REGULAR = "NotoNaskhArabic"
_FONT_BOLD = "NotoNaskhArabic-Bold"
_ASSETS_DIR = Path(__file__).resolve().parent / "assets"

_HEADLINE_LABELS: dict[str, str] = {
    "total_waste_amount": "إجمالي الهدر المالي",
    "waste_percentage": "نسبة الهدر",
    "potential_savings_amount": "الوفورات المحتملة",
    "active_savings_opportunities": "فرص التوفير النشطة",
}

# Brand palette
_NAVY = colors.HexColor("#0D2137")
_GOLD = colors.HexColor("#B8860B")
_LIGHT = colors.HexColor("#F4F6F8")
_BORDER = colors.HexColor("#DDE3EA")
_TEXT = colors.HexColor("#1A1A1A")
_MUTED = colors.HexColor("#5A6570")
_HIGH = colors.HexColor("#C0392B")
_MED = colors.HexColor("#E67E22")
_LOW = colors.HexColor("#27AE60")


def render_executive_pdf(
    content: dict[str, Any],
    *,
    report_title: str,
    platform_name: str,
    report_language: str,
    include_cover_page: bool,
) -> bytes:
    """Six-page board-ready layout from persisted report content."""
    del include_cover_page  # cover always included in executive layout
    _register_fonts()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4, invariant=1)
    width, height = A4
    margin = 48
    sections = _index_sections(content.get("sections") or [])
    cover = sections.get("cover", {})
    is_ar = report_language.lower().startswith("ar")

    # --- Page 1: Cover + Executive Summary ---
    _draw_page_frame(pdf, width, height, margin, page=1, is_ar=is_ar)
    y = height - margin - 10
    y = _draw_text_block(
        pdf, report_title, margin, y, width - margin,
        font=_FONT_BOLD, size=22, color=_NAVY, is_ar=is_ar, align="right" if is_ar else "left",
    )
    y -= 12
    y = _draw_text_block(
        pdf, platform_name, margin, y, width - margin,
        font=_FONT_REGULAR, size=12, color=_GOLD, is_ar=is_ar,
    )
    y = _draw_text_block(
        pdf, "أعدّ بواسطة Khazina — منصة الذكاء المالي التنفيذي", margin, y, width - margin,
        font=_FONT_REGULAR, size=9, color=_MUTED, is_ar=is_ar,
    )
    for label, key in (
        ("المؤسسة", "organization_name"),
        ("فترة التقرير", "period_label"),
        ("تاريخ التحليل", "completed_at"),
        ("ملف المصدر", "source_file_name"),
    ):
        val = cover.get(key) or (content.get("generated_at") if key == "completed_at" else None)
        if val:
            y = _draw_text_block(
                pdf, f"{label}: {val}", margin, y, width - margin,
                font=_FONT_REGULAR, size=10, color=_MUTED, is_ar=is_ar,
            )
    y -= 8
    pdf.setStrokeColor(_GOLD)
    pdf.setLineWidth(2)
    pdf.line(margin, y, width - margin, y)
    y -= 24
    y = _draw_section_heading(pdf, "الملخص التنفيذي", margin, y, width - margin, is_ar)
    summary = sections.get("executive_summary", {}).get("text", "")
    if summary:
        y = _draw_paragraph(
            pdf, sanitize_executive_text(str(summary)), margin, y, width - 2 * margin, is_ar, size=11,
        )
    highlights = sections.get("decision_highlights", {}).get("items") or []
    if highlights:
        y -= 10
        y = _draw_section_heading(pdf, "أبرز القرارات", margin, y, width - margin, is_ar, size=12)
        for item in highlights[:3]:
            line = f"• {item.get('decision') or item.get('title', '')}"
            if item.get("executive_angle"):
                line = f"• [{item.get('executive_angle')}] {item.get('decision') or item.get('title', '')}"
            y = _draw_text_block(
                pdf, sanitize_executive_text(str(line)), margin, y, width - margin,
                font=_FONT_REGULAR, size=9, color=_TEXT, is_ar=is_ar,
            )
    pdf.showPage()

    # --- Page 2: KPI cards + charts ---
    _draw_page_frame(pdf, width, height, margin, page=2, is_ar=is_ar)
    y = height - margin - 10
    y = _draw_section_heading(pdf, "المؤشرات التنفيذية", margin, y, width - margin, is_ar)
    metrics = _executive_metrics(sections.get("key_metrics", {}))
    card_w = (width - 2 * margin - 20) / 3
    card_h = 72
    x0 = margin
    y_cards = y - card_h
    labels_vals = list(metrics.items())[:3] if metrics else []
    if not labels_vals:
        headline = sections.get("key_metrics", {}).get("headline") or {}
        labels_vals = [
            (_HEADLINE_LABELS.get(k, k), v) for k, v in headline.items()
        ][:3]
    colors_kpi = [_NAVY, _GOLD, _HIGH]
    for i, (lbl, val) in enumerate(labels_vals):
        cx = x0 + i * (card_w + 10)
        _draw_kpi_card(pdf, cx, y_cards, card_w, card_h, str(lbl), _fmt_val(val), colors_kpi[i % 3], is_ar)
    y = y_cards - 30
    waste = sections.get("waste_analysis", {})
    breakdowns = waste.get("category_breakdowns") or []
    if breakdowns:
        y = _draw_section_heading(pdf, "توزيع الهدر حسب الفئة", margin, y, width - margin, is_ar, size=12)
        _draw_pie_chart(
            pdf, margin + 40, y - 100, 80,
            [(_category_display(b), float(b.get("percentage") or b.get("amount") or 1)) for b in breakdowns[:6]],
            is_ar,
        )
        _draw_bar_chart(
            pdf, margin + 180, y - 110, width - margin - 180, 100,
            [(_category_display(b), float(b.get("amount") or 0)) for b in breakdowns[:5]],
            is_ar,
        )
    top_opportunity = breakdowns[0] if breakdowns else None
    if top_opportunity:
        y -= 120
        y = _draw_text_block(
            pdf,
            f"أبرز فرصة: {_category_display(top_opportunity)} — {_fmt_val(top_opportunity.get('amount'))}",
            margin, y, width - margin, font=_FONT_BOLD, size=10, color=_NAVY, is_ar=is_ar,
        )
    pdf.showPage()

    # --- Page 3: Waste analysis table ---
    _draw_page_frame(pdf, width, height, margin, page=3, is_ar=is_ar)
    y = height - margin - 10
    y = _draw_section_heading(pdf, "تحليل الهدر", margin, y, width - margin, is_ar)
    commentary = waste.get("executive_commentary")
    if commentary:
        y = _draw_paragraph(
            pdf, sanitize_executive_text(str(commentary)), margin, y, width - 2 * margin, is_ar, size=10,
        )
        y -= 8
    if breakdowns:
        rows = [
            (
                _category_display(b),
                _fmt_val(b.get("amount")),
                f"{float(b.get('percentage') or 0):.1f}%",
                str(b.get("priority_rank") or "—"),
            )
            for b in breakdowns
        ]
        y = _draw_table(
            pdf, margin, y - 10, width - 2 * margin,
            headers=("الفئة", "المبلغ", "النسبة", "الأولوية"),
            rows=rows,
            is_ar=is_ar,
        )
    pdf.showPage()

    # --- Page 4: Risk analysis ---
    _draw_page_frame(pdf, width, height, margin, page=4, is_ar=is_ar)
    y = height - margin - 10
    y = _draw_section_heading(pdf, "تحليل المخاطر", margin, y, width - margin, is_ar)
    risk_text = (
        sections.get("risk_summary", {}).get("text")
        or sections.get("risk_explanation", {}).get("text")
        or sections.get("top_risks", {}).get("summary")
    )
    top_risks = sections.get("top_risks", {}).get("items") or sections.get("top_risks", {}).get("risks") or []
    if risk_text:
        y = _draw_paragraph(
            pdf, sanitize_executive_text(str(risk_text)), margin, y, width - 2 * margin, is_ar, size=10,
        )
        y -= 12
    if top_risks:
        rows = []
        for r in top_risks[:8]:
            if isinstance(r, dict):
                rows.append((
                    str(r.get("name") or r.get("title") or "—"),
                    str(r.get("score") or r.get("priority") or "—"),
                    str(r.get("status") or r.get("category") or "—"),
                ))
        if rows:
            _draw_table(
                pdf, margin, y - 10, width - 2 * margin,
                headers=("المخاطرة", "الدرجة", "الحالة"),
                rows=rows,
                is_ar=is_ar,
                row_color_fn=_risk_row_color,
            )
    elif not risk_text:
        _draw_paragraph(
            pdf, "لا تتوفر بيانات مخاطر مفصّلة في هذا التقرير.",
            margin, y, width - 2 * margin, is_ar, size=10, color=_MUTED,
        )
    pdf.showPage()

    # --- Page 5: Recommendation cards ---
    _draw_page_frame(pdf, width, height, margin, page=5, is_ar=is_ar)
    y = height - margin - 10
    y = _draw_section_heading(pdf, "التوصيات التنفيذية", margin, y, width - margin, is_ar)
    rec_items = sections.get("recommendations", {}).get("items") or []
    card_h = 118
    for item in rec_items[:5]:
        if y < margin + card_h + 40:
            pdf.showPage()
            _draw_page_frame(pdf, width, height, margin, page=5, is_ar=is_ar)
            y = height - margin - 10
        body = f"الإجراء المقترح:\n{item.get('title','')}\n{item.get('description','')}"
        exec_ctx = (item.get("source_context") or {}).get("executive") if isinstance(item.get("source_context"), dict) else None
        if exec_ctx:
            fields = ExecutiveRecommendationFields(
                problem=str(exec_ctx.get("problem", "")),
                evidence=str(exec_ctx.get("evidence", "")),
                business_impact=str(exec_ctx.get("business_impact", "")),
                root_cause=str(exec_ctx.get("root_cause", exec_ctx.get("why", ""))),
                recommendation=str(exec_ctx.get("recommendation") or exec_ctx.get("action", "")),
                priority_label=str(exec_ctx.get("priority_label", "")),
                timeline=str(exec_ctx.get("timeline", "")),
                owner_department=str(exec_ctx.get("owner_department", "")),
                expected_savings=str(exec_ctx.get("expected_savings", "")),
                success_kpi=str(exec_ctx.get("success_kpi", "")),
                why=str(exec_ctx.get("why", "")),
                executive_angle=str(exec_ctx.get("executive_angle", "")),
                executive_decision=str(exec_ctx.get("executive_decision", "")),
                priority_rationale=str(exec_ctx.get("priority_rationale", "")),
            )
        else:
            fields = parse_executive_recommendation(body)
        priority = str(item.get("priority") or "medium")
        y = _draw_recommendation_card(
            pdf, margin, y - card_h - 8, width - 2 * margin, card_h,
            fields, priority, is_ar,
        )
        y -= card_h + 8
    pdf.showPage()

    # --- Page 6: Implementation roadmap ---
    _draw_page_frame(pdf, width, height, margin, page=6, is_ar=is_ar)
    y = height - margin - 10
    y = _draw_section_heading(pdf, "خارطة التنفيذ", margin, y, width - margin, is_ar)
    savings = metrics.get("الوفورات المحتملة") or metrics.get(_HEADLINE_LABELS.get("potential_savings_amount", ""))
    if savings:
        y = _draw_text_block(
            pdf, f"العائد المتوقع على الاستثمار: {_fmt_val(savings)}",
            margin, y, width - margin, font=_FONT_BOLD, size=11, color=_NAVY, is_ar=is_ar,
        )
        y -= 16
    phases = [
        ("30 يوماً", "إجراءات فورية عالية الأولوية", _HIGH),
        ("60 يوماً", "تدعيم الضوابط والمراقبة", _MED),
        ("90 يوماً", "تحسين مستمر وقياس الأثر", _LOW),
    ]
    phase_w = (width - 2 * margin - 20) / 3
    for i, (period, desc, col) in enumerate(phases):
        px = margin + i * (phase_w + 10)
        _draw_roadmap_card(pdf, px, y - 100, phase_w, 100, period, desc, col, is_ar)
    y -= 120
    _draw_paragraph(
        pdf,
        sanitize_executive_text(
            "الخلاصة التنفيذية: تنفيذ القرارات عالية الأولوية خلال 30 يوماً "
            "يحقق أسرع عائد على الاستثمار. خزينة — شريككم في القرار المالي."
        ),
        margin, y, width - 2 * margin, is_ar, size=10, color=_NAVY,
    )
    pdf.showPage()

    pdf.save()
    return buffer.getvalue()


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


def _prepare_text(text: str, *, report_language: str) -> str:
    raw = str(text).replace("\n", " ").strip()
    if not raw:
        return ""
    if not report_language.lower().startswith("ar"):
        return raw
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        return get_display(arabic_reshaper.reshape(raw))
    except Exception:
        return raw


def _executive_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    headline = payload.get("headline")
    if isinstance(headline, dict) and headline:
        return {_HEADLINE_LABELS.get(k, k): v for k, v in headline.items()}
    return {}


def _index_sections(sections: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for section in sections:
        key = str(section.get("key", ""))
        if key:
            out[key] = dict(section.get("payload") or {})
    return out


def _category_display(item: dict[str, Any]) -> str:
    label = item.get("category_label_ar")
    if label:
        return str(label)
    name = item.get("category_name", "")
    return category_label_ar(str(name)) if name else "—"


def _fmt_val(val: Any) -> str:
    if val is None:
        return "—"
    if isinstance(val, float):
        if val >= 1_000_000:
            return f"{val / 1_000_000:.2f}M ر.س"
        if val >= 1_000:
            return f"{val / 1_000:.0f}K ر.س"
        return f"{val:,.0f} ر.س"
    return str(val)


def _draw_page_frame(pdf: canvas.Canvas, width: float, height: float, margin: float, *, page: int, is_ar: bool) -> None:
    pdf.setFillColor(_NAVY)
    pdf.rect(0, height - 28, width, 28, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont(_FONT_REGULAR, 9)
    footer = f"صفحة {page}" if is_ar else f"Page {page}"
    pdf.drawCentredString(width / 2, 22, _prepare_text(footer, report_language="ar" if is_ar else "en"))
    pdf.drawRightString(width - margin, height - 20, _prepare_text("خزينة — تقرير تنفيذي", report_language="ar" if is_ar else "en"))


def _draw_section_heading(pdf: canvas.Canvas, text: str, x: float, y: float, x2: float, is_ar: bool, size: int = 14) -> float:
    pdf.setFillColor(_NAVY)
    pdf.setFont(_FONT_BOLD, size)
    prepared = _prepare_text(text, report_language="ar" if is_ar else "en")
    if is_ar:
        pdf.drawRightString(x2, y, prepared)
    else:
        pdf.drawString(x, y, prepared)
    pdf.setStrokeColor(_GOLD)
    pdf.setLineWidth(1.5)
    pdf.line(x, y - 6, x2, y - 6)
    return y - 22


def _draw_text_block(
    pdf: canvas.Canvas, text: str, x: float, y: float, x2: float, *,
    font: str, size: int, color: colors.Color, is_ar: bool, align: str = "right",
) -> float:
    pdf.setFillColor(color)
    pdf.setFont(font, size)
    prepared = _prepare_text(text, report_language="ar" if is_ar else "en")
    if align == "right" and is_ar:
        pdf.drawRightString(x2, y, prepared[:120])
    else:
        pdf.drawString(x, y, prepared[:120])
    return y - size - 6


def _draw_paragraph(
    pdf: canvas.Canvas, text: str, x: float, y: float, max_w: float, is_ar: bool,
    *, size: int = 10, color: colors.Color = _TEXT,
) -> float:
    pdf.setFillColor(color)
    pdf.setFont(_FONT_REGULAR, size)
    for line in textwrap.wrap(text, width=70):
        prepared = _prepare_text(line, report_language="ar" if is_ar else "en")
        if is_ar:
            pdf.drawRightString(x + max_w, y, prepared)
        else:
            pdf.drawString(x, y, prepared)
        y -= size + 4
        if y < 60:
            break
    return y


def _draw_kpi_card(pdf: canvas.Canvas, x: float, y: float, w: float, h: float, label: str, value: str, accent: colors.Color, is_ar: bool) -> None:
    pdf.setFillColor(_LIGHT)
    pdf.setStrokeColor(_BORDER)
    pdf.roundRect(x, y, w, h, 6, fill=1, stroke=1)
    pdf.setFillColor(accent)
    pdf.rect(x, y + h - 4, w, 4, fill=1, stroke=0)
    pdf.setFillColor(_MUTED)
    pdf.setFont(_FONT_REGULAR, 9)
    pdf.drawCentredString(x + w / 2, y + h - 22, _prepare_text(label, report_language="ar" if is_ar else "en")[:40])
    pdf.setFillColor(_NAVY)
    pdf.setFont(_FONT_BOLD, 14)
    pdf.drawCentredString(x + w / 2, y + 28, _prepare_text(value, report_language="ar" if is_ar else "en")[:30])


def _draw_pie_chart(pdf: canvas.Canvas, cx: float, cy: float, r: float, slices: list[tuple[str, float]], is_ar: bool) -> None:
    total = sum(v for _, v in slices) or 1
    palette = [_NAVY, _GOLD, _HIGH, _MED, _LOW, _MUTED]
    start = 0.0
    for i, (_label, val) in enumerate(slices):
        extent = 360 * (val / total)
        pdf.setFillColor(palette[i % len(palette)])
        pdf.wedge(cx - r, cy - r, cx + r, cy + r, start, start + extent, fill=1)
        start += extent


def _draw_bar_chart(pdf: canvas.Canvas, x: float, y: float, w: float, h: float, bars: list[tuple[str, float]], is_ar: bool) -> None:
    if not bars:
        return
    max_v = max(v for _, v in bars) or 1
    bar_w = w / max(len(bars), 1) - 8
    for i, (label, val) in enumerate(bars):
        bh = (val / max_v) * h
        bx = x + i * (bar_w + 8)
        pdf.setFillColor(_NAVY)
        pdf.rect(bx, y, bar_w, bh, fill=1, stroke=0)
        pdf.setFillColor(_MUTED)
        pdf.setFont(_FONT_REGULAR, 7)
        pdf.drawCentredString(bx + bar_w / 2, y - 10, _prepare_text(str(label)[:12], report_language="ar" if is_ar else "en"))


def _draw_table(
    pdf: canvas.Canvas, x: float, y: float, w: float, *,
    headers: tuple[str, ...], rows: list[tuple[str, ...]], is_ar: bool,
    row_color_fn=None,
) -> float:
    col_w = w / len(headers)
    row_h = 22
    pdf.setFillColor(_NAVY)
    pdf.rect(x, y - row_h, w, row_h, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont(_FONT_BOLD, 9)
    for i, h in enumerate(headers):
        cx = x + w - (i + 0.5) * col_w if is_ar else x + (i + 0.5) * col_w
        pdf.drawCentredString(cx, y - 15, _prepare_text(h, report_language="ar" if is_ar else "en"))
    y -= row_h
    for ri, row in enumerate(rows):
        bg = _LIGHT if ri % 2 == 0 else colors.white
        if row_color_fn:
            bg = row_color_fn(row) or bg
        pdf.setFillColor(bg)
        pdf.rect(x, y - row_h, w, row_h, fill=1, stroke=0)
        pdf.setStrokeColor(_BORDER)
        pdf.rect(x, y - row_h, w, row_h, fill=0, stroke=1)
        pdf.setFillColor(_TEXT)
        pdf.setFont(_FONT_REGULAR, 8)
        for i, cell in enumerate(row):
            cx = x + w - (i + 0.5) * col_w if is_ar else x + (i + 0.5) * col_w
            pdf.drawCentredString(cx, y - 15, _prepare_text(str(cell)[:28], report_language="ar" if is_ar else "en"))
        y -= row_h
    return y


def _risk_row_color(row: tuple[str, ...]) -> colors.Color | None:
    score = row[1] if len(row) > 1 else ""
    if any(w in str(score) for w in ("مرتفع", "high", "عال")):
        return colors.HexColor("#FDEDEC")
    return None


def _priority_color(priority: str) -> colors.Color:
    p = priority.lower()
    if p == "high":
        return _HIGH
    if p == "low":
        return _LOW
    return _MED


def _draw_recommendation_card(
    pdf: canvas.Canvas, x: float, y: float, w: float, h: float,
    fields: ExecutiveRecommendationFields, priority: str, is_ar: bool,
) -> float:
    col = _priority_color(priority)
    pdf.setFillColor(_LIGHT)
    pdf.setStrokeColor(_BORDER)
    pdf.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    pdf.setFillColor(col)
    pdf.rect(x, y + h - 6, w, 6, fill=1, stroke=0)
    pdf.setFillColor(_NAVY)
    pdf.setFont(_FONT_BOLD, 10)
    title = _prepare_text(fields.recommendation[:90], report_language="ar" if is_ar else "en")
    pdf.drawRightString(x + w - 12, y + h - 22, title) if is_ar else pdf.drawString(x + 12, y + h - 22, title)
    pdf.setFont(_FONT_REGULAR, 8)
    pdf.setFillColor(_TEXT)
    lines = [
        f"الزاوية: {fields.executive_angle}" if fields.executive_angle else "",
        f"المشكلة: {fields.problem[:80]}" if fields.problem else "",
        f"الدليل: {fields.evidence[:80]}" if fields.evidence else "",
        f"لماذا الأولوية: {fields.priority_rationale[:70]}" if fields.priority_rationale else "",
        f"القرار: {fields.executive_decision[:80]}" if fields.executive_decision else "",
        f"الأثر: {fields.business_impact}" if fields.business_impact else "",
        f"النتيجة: {fields.expected_savings}" if fields.expected_savings else "",
        f"مؤشر النجاح: {fields.success_kpi[:60]}" if fields.success_kpi else "",
        f"المدة: {fields.timeline} | المسؤول: {fields.owner_department}" if fields.timeline or fields.owner_department else "",
    ]
    ly = y + h - 38
    for line in lines:
        if not line.strip():
            continue
        prepared = _prepare_text(line[:100], report_language="ar" if is_ar else "en")
        if is_ar:
            pdf.drawRightString(x + w - 12, ly, prepared)
        else:
            pdf.drawString(x + 12, ly, prepared)
        ly -= 12
    return y


def _draw_roadmap_card(pdf: canvas.Canvas, x: float, y: float, w: float, h: float, period: str, desc: str, accent: colors.Color, is_ar: bool) -> None:
    pdf.setFillColor(_LIGHT)
    pdf.setStrokeColor(_BORDER)
    pdf.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    pdf.setFillColor(accent)
    pdf.circle(x + w / 2, y + h - 24, 10, fill=1)
    pdf.setFillColor(_NAVY)
    pdf.setFont(_FONT_BOLD, 11)
    pdf.drawCentredString(x + w / 2, y + h - 50, _prepare_text(period, report_language="ar" if is_ar else "en"))
    pdf.setFont(_FONT_REGULAR, 9)
    pdf.setFillColor(_TEXT)
    for i, line in enumerate(textwrap.wrap(desc, width=24)):
        pdf.drawCentredString(x + w / 2, y + h - 68 - i * 12, _prepare_text(line, report_language="ar" if is_ar else "en"))
