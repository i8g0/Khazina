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

    lines = ["## سياق التحليل الحتمي (Deterministic Risk Context)", ""]
    lines.append("### ملخص التحليل")
    lines.append(f"- إجمالي النتائج: {analysis.get('total_findings', 0)}")
    lines.append(f"- عالية الأولوية: {analysis.get('high_priority_count', 0)}")
    lines.append(f"- متوسطة الأولوية: {analysis.get('medium_priority_count', 0)}")
    lines.append(f"- منخفضة الأولوية: {analysis.get('low_priority_count', 0)}")
    lines.append(
        f"- مستوى الوضع العام: {analysis.get('overall_posture_level', 'unknown')}"
    )
    if analysis.get("top_category_code"):
        lines.append(f"- أبرز فئة: {analysis['top_category_code']}")
    if analysis.get("liquidity_ratio") is not None:
        lines.append(f"- نسبة السيولة: {analysis['liquidity_ratio']}")
    if analysis.get("waste_percentage") is not None:
        lines.append(f"- نسبة الهدر: {analysis['waste_percentage']}%")

    if findings:
        lines.extend(["", "### أبرز النتائج المكتشفة (مرتبة حسب الأولوية)", ""])
        for item in findings[:10]:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- [{item.get('finding_id', '?')}] "
                f"{item.get('name', '')} | "
                f"فئة={item.get('category_code', '')} | "
                f"درجة={item.get('score', '')} | "
                f"أولوية={item.get('priority', '')} | "
                f"احتمال={item.get('likelihood', '')} | "
                f"أثر={item.get('impact', '')}"
            )
            rule_id = item.get("detection_rule_id")
            if rule_id:
                lines.append(f"  - قاعدة الكشف: {rule_id}")

    register = runtime_metadata.get("risk_register_context") or {}
    if isinstance(register, dict) and register:
        lines.extend(["", "### سياق السجل (Register Metadata)", ""])
        for key, value in register.items():
            lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "### قيود مهمة",
            "- النتائج أعلاه محسوبة حتمياً بواسطة Risk Engine.",
            "- لا تُعدّل الدرجات أو الفئات أو الأولويات أو حالات دورة الحياة.",
            "- دورك: الشرح والتوصية والتلخيص التنفيذي فقط.",
            "",
        ]
    )
    return "\n".join(lines)
