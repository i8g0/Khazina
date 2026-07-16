"""Build deterministic risk metadata supplement for prompts (Sprint 9.5).

Consumes plain dict structures from ``analysis_runs.runtime_metadata`` only —
no ORM models or database objects.
"""

from __future__ import annotations

from typing import Any


def build_risk_metadata_supplement(runtime_metadata: dict[str, Any]) -> str:
    """Format risk analysis summary and findings for prompt context."""
    analysis = runtime_metadata.get("risk_analysis") or {}
    findings = runtime_metadata.get("risk_findings") or []
    if not isinstance(findings, list):
        findings = []

    lines = ["## سياق التحليل المالي الحتمي", ""]
    lines.append("### ملخص التحليل")
    lines.append(f"- إجمالي النتائج: {analysis.get('total_findings', 0)}")
    lines.append(f"- عالية الأولوية: {analysis.get('high_priority_count', 0)}")
    lines.append(f"- متوسطة الأولوية: {analysis.get('medium_priority_count', 0)}")
    lines.append(f"- منخفضة الأولوية: {analysis.get('low_priority_count', 0)}")
    posture = analysis.get("overall_posture_level", "")
    lines.append(f"- الوضع العام: {posture}")
    if analysis.get("top_category_code"):
        lines.append(f"- أبرز فئة: {analysis['top_category_code']}")
    if analysis.get("liquidity_ratio") is not None:
        lines.append(f"- نسبة السيولة: {analysis['liquidity_ratio']}")
    if analysis.get("waste_percentage") is not None:
        lines.append(f"- نسبة الهدر: {analysis['waste_percentage']}%")

    if findings:
        lines.extend(["", "### أبرز المخاطر (من البيانات المرفوعة)", ""])
        for item in findings[:10]:
            if not isinstance(item, dict):
                continue
            evidence = item.get("evidence") if isinstance(item.get("evidence"), dict) else {}
            lines.append(
                f"- {item.get('name', '')} | "
                f"درجة={item.get('score', '')} | "
                f"أولوية={item.get('priority', '')} | "
                f"احتمال={item.get('likelihood', '')} | "
                f"أثر={item.get('impact', '')}"
            )
            if evidence.get("department_ar"):
                lines.append(f"  - الإدارة: {evidence['department_ar']}")
            if evidence.get("supplier_ar") and evidence.get("supplier_ar") != "—":
                lines.append(f"  - المورد: {evidence['supplier_ar']}")
            if evidence.get("amount_exposed_label"):
                lines.append(f"  - المبلغ المعرّض: {evidence['amount_exposed_label']}")
            if evidence.get("estimated_savings_label"):
                lines.append(f"  - التوفير المتوقع: {evidence['estimated_savings_label']}")
            if evidence.get("recommended_action_ar"):
                lines.append(f"  - الإجراء: {evidence['recommended_action_ar']}")
            if evidence.get("if_ignored_ar"):
                lines.append(f"  - إذا تجاهلناه: {evidence['if_ignored_ar']}")

    register = runtime_metadata.get("risk_register_context") or {}
    if isinstance(register, dict) and register:
        lines.extend(["", "### سياق سجل المخاطر", ""])
        for key, value in register.items():
            lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "### قيود مهمة",
            "- النتائج أعلاه محسوبة من البيانات المرفوعة — لا تُعدّل الدرجات أو الأولويات.",
            "- دورك: مستشار استراتيجي — اشرح الدليل والأثر المالي والتوصية والمالك والإطار الزمني.",
            "",
        ]
    )
    return "\n".join(lines)
