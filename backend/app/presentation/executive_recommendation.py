"""Parse and format McKinsey-style executive recommendations."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.presentation.executive_sanitize import sanitize_executive_text

_FIELD_SPECS: tuple[tuple[str, str], ...] = (
    ("executive_angle", r"الزاوية\s*التنفيذية\s*:\s*"),
    ("problem", r"المشكلة\s*:\s*"),
    ("evidence", r"(?:الأدلة|الدليل|الأدلة\s*الداعمة)\s*:\s*"),
    ("business_impact", r"الأثر(?:\s*على\s*الأعمال|\s*التجاري|\s*المالي)?\s*:\s*"),
    ("root_cause", r"(?:السبب\s*الجذري|السبب)\s*:\s*"),
    ("executive_decision", r"القرار\s*:\s*"),
    ("recommendation", r"(?:التوصية\s*التنفيذية|الإجراء(?:\s*المقتر[ح]?)?|ماذا\s*يفعل\s*الإدارة)\s*:\s*"),
    ("priority_rationale", r"لماذا\s*الأولوية\s*:\s*"),
    ("priority_label", r"الأولوية\s*:\s*"),
    ("owner_department", r"(?:المسؤول|الإدارة\s*المسؤولة|الجهة\s*المسؤولة|المالك)\s*:\s*"),
    ("timeline", r"(?:المدة\s*الزمنية|الجدول\s*الزمني|الإطار\s*الزمني|الإطار\s*التنفيذي)\s*:\s*"),
    ("expected_savings", r"(?:الوفورات\s*المتوقعة|التوفير\s*المتوقع|النتيجة\s*المتوقعة|الوفورات)\s*:\s*"),
    ("success_kpi", r"(?:مؤشر\s*النجاح|مؤشر\s*الأداء)\s*:\s*"),
    ("why", r"(?:لماذا|المبرر)\s*:\s*"),
)

_NEXT_FIELD = re.compile(
    r"\n\s*(?:"
    r"الزاوية\s*التنفيذية|المشكلة|الأدلة|الدليل|السبب|القرار|التوصية|الإجراء|ماذا\s*يفعل|"
    r"لماذا\s*الأولوية|لماذا|المبرر|الأثر|الوفورات|التوفير|النتيجة|الأولوية|"
    r"المدة\s*الزمنية|الجدول\s*الزمني|الإطار\s*الزمني|الإطار\s*التنفيذي|"
    r"المسؤول|الإدارة\s*المسؤولة|الجهة\s*المسؤولة|مؤشر\s*النجاح|مؤشر\s*الأداء"
    r")\s*:",
    re.UNICODE,
)


@dataclass(frozen=True, slots=True)
class ExecutiveRecommendationFields:
    problem: str
    evidence: str
    business_impact: str
    root_cause: str
    recommendation: str
    priority_label: str
    timeline: str
    owner_department: str
    expected_savings: str
    success_kpi: str
    why: str = ""
    executive_angle: str = ""
    executive_decision: str = ""
    priority_rationale: str = ""

    @property
    def action(self) -> str:
        return self.recommendation

    def to_description(self) -> str:
        lines: list[str] = []
        if self.executive_angle:
            lines.append(f"الزاوية التنفيذية: {self.executive_angle}")
        if self.problem:
            lines.append(f"المشكلة: {self.problem}")
        if self.evidence:
            lines.append(f"الدليل:\n{self.evidence}")
        if self.priority_rationale:
            lines.append(f"لماذا الأولوية: {self.priority_rationale}")
        if self.root_cause or self.why:
            lines.append(f"السبب الجذري: {self.root_cause or self.why}")
        if self.executive_decision and self.executive_decision != self.recommendation:
            lines.append(f"القرار: {self.executive_decision}")
        if self.business_impact:
            lines.append(f"الأثر على الأعمال: {self.business_impact}")
        if self.priority_label:
            lines.append(f"الأولوية: {self.priority_label}")
        if self.expected_savings:
            lines.append(f"النتيجة المتوقعة: {self.expected_savings}")
        if self.timeline:
            lines.append(f"المدة الزمنية: {self.timeline}")
        if self.owner_department:
            lines.append(f"الإدارة المسؤولة: {self.owner_department}")
        if self.success_kpi:
            lines.append(f"مؤشر النجاح: {self.success_kpi}")
        return "\n".join(lines) if lines else self.recommendation

    def to_dict(self) -> dict[str, str]:
        return {
            "executive_angle": self.executive_angle,
            "problem": self.problem,
            "evidence": self.evidence,
            "business_impact": self.business_impact,
            "root_cause": self.root_cause,
            "recommendation": self.recommendation,
            "executive_decision": self.executive_decision or self.recommendation,
            "action": self.recommendation,
            "priority_rationale": self.priority_rationale,
            "priority_label": self.priority_label,
            "timeline": self.timeline,
            "owner_department": self.owner_department,
            "expected_savings": self.expected_savings,
            "success_kpi": self.success_kpi,
            "why": self.why or self.root_cause,
        }


def parse_executive_recommendation(body: str) -> ExecutiveRecommendationFields:
    raw = body.strip()
    values: dict[str, str] = {}

    for key, prefix_pattern in _FIELD_SPECS:
        match = re.search(prefix_pattern + r"(.*)", raw, re.DOTALL | re.UNICODE)
        if not match:
            continue
        chunk = match.group(1)
        end = _NEXT_FIELD.search(chunk)
        value = chunk[: end.start()].strip() if end else chunk.strip()
        values[key] = sanitize_executive_text(value)

    recommendation = values.get("recommendation") or values.get("executive_decision", "")
    if not recommendation and values.get("why"):
        recommendation = values.get("why", "")

    if not recommendation:
        first_line = raw.split("\n", 1)[0].strip()
        recommendation = sanitize_executive_text(re.sub(r"^\d+\.\s*", "", first_line))

    root_cause = values.get("root_cause", "")
    why = values.get("why", "")
    if not root_cause and why:
        root_cause = why

    evidence = values.get("evidence", "")
    if not evidence:
        evidence = _extract_structured_evidence(raw)

    return ExecutiveRecommendationFields(
        problem=values.get("problem", ""),
        evidence=evidence,
        business_impact=values.get("business_impact", ""),
        root_cause=root_cause,
        recommendation=recommendation,
        priority_label=values.get("priority_label", ""),
        timeline=values.get("timeline", ""),
        owner_department=values.get("owner_department", ""),
        expected_savings=values.get("expected_savings", ""),
        success_kpi=values.get("success_kpi", ""),
        why=why,
        executive_angle=values.get("executive_angle", ""),
        executive_decision=values.get("executive_decision", recommendation),
        priority_rationale=values.get("priority_rationale", ""),
    )


def _extract_structured_evidence(raw: str) -> str:
    match = re.search(
        r"(?:الدليل|الأدلة)\s*:\s*(.+?)(?=\n\s*(?:القرار|التوصية|الأثر|لماذا\s*الأولوية)|$)",
        raw,
        re.DOTALL | re.UNICODE,
    )
    if not match:
        return ""
    block = match.group(1).strip()
    required = ("الفئة:", "الفترة:", "قيمة الهدر:", "النسبة:")
    if all(token in block for token in required):
        return sanitize_executive_text(block)
    return sanitize_executive_text(block)


def map_priority_from_label(label: str, body: str) -> str:
    text = f"{label} {body}".lower()
    if any(w in text for w in ("عالية", "مرتفع", "high", "حرج", "فوري")):
        return "high"
    if any(w in text for w in ("منخفض", "low")):
        return "low"
    return "medium"
