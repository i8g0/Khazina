"""Risk context loader for simulation — connects Risk → Simulation workflow."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.db.models.enums import AnalysisType
from app.presentation.business_labels import risk_category_ar, risk_posture_ar, risk_priority_ar
from app.presentation.executive_sanitize import sanitize_executive_text
from app.repositories import AnalysisRepository, RecommendationRepository, RiskAnalysisRepository
from app.services.exceptions import InvalidStateError, ResourceNotFoundError


@dataclass(frozen=True, slots=True)
class SimulationRiskContext:
    """Executive risk snapshot consumed by AI simulation interpreter/explainer."""

    analysis_run_id: str
    posture_ar: str
    total_findings: int
    high_priority_count: int
    narrative_summary: str
    top_risks: tuple[dict[str, Any], ...]
    recommendations: tuple[str, ...]
    departments_exposed: tuple[str, ...]
    suppliers_exposed: tuple[str, ...]

    def to_prompt_block(self) -> str:
        lines = [
            "سياق المخاطر الحالي (من تحليل المخاطر المرتبط):",
            f"- الوضع العام: {self.posture_ar}",
            f"- إجمالي المخاطر: {self.total_findings} (عالية: {self.high_priority_count})",
            self.narrative_summary,
        ]
        if self.departments_exposed:
            lines.append(f"- الإدارات المتأثرة: {', '.join(self.departments_exposed[:8])}")
        if self.suppliers_exposed:
            lines.append(f"- الموردون ذوو التعرّض: {', '.join(self.suppliers_exposed[:8])}")
        if self.top_risks:
            lines.append("- أبرز المخاطر:")
            for item in self.top_risks[:5]:
                lines.append(
                    f"  • {item['title']} — {item.get('exposure', '')} "
                    f"({item.get('priority', '')})"
                )
        if self.recommendations:
            lines.append("- توصيات تنفيذية مرتبطة:")
            for rec in self.recommendations[:5]:
                lines.append(f"  • {rec}")
        lines.append(
            "عند شرح السيناريو: اربط النتائج بهذه المخاطر وبيّن كيف ستؤثر على التعرّض المالي."
        )
        return "\n".join(lines)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "analysis_run_id": self.analysis_run_id,
            "posture_ar": self.posture_ar,
            "total_findings": self.total_findings,
            "high_priority_count": self.high_priority_count,
            "narrative_summary": self.narrative_summary,
            "top_risks": list(self.top_risks),
            "recommendations": list(self.recommendations),
            "departments_exposed": list(self.departments_exposed),
            "suppliers_exposed": list(self.suppliers_exposed),
        }


def load_simulation_risk_context(
    *,
    organization_id: uuid.UUID,
    risk_analysis_run_id: uuid.UUID,
    analysis_repository: AnalysisRepository,
    risk_analysis_repository: RiskAnalysisRepository,
    recommendation_repository: RecommendationRepository | None = None,
) -> SimulationRiskContext:
    run = analysis_repository.get(risk_analysis_run_id)
    if run is None:
        raise ResourceNotFoundError("AnalysisRun", risk_analysis_run_id)
    if run.organization_id != organization_id:
        raise ResourceNotFoundError("AnalysisRun", risk_analysis_run_id)
    if run.analysis_type != AnalysisType.RISK:
        raise InvalidStateError(
            f"risk_analysis_run_id must reference a risk analysis run (got {run.analysis_type})"
        )

    result = risk_analysis_repository.get_result_for_run(risk_analysis_run_id)
    findings = risk_analysis_repository.list_findings(risk_analysis_run_id, limit=20)

    posture = risk_posture_ar(result.overall_posture_level if result else "moderate")
    total = result.total_findings if result else len(findings)
    high = result.high_priority_count if result else sum(
        1 for f in findings if f.priority == "high"
    )

    departments: list[str] = []
    suppliers: list[str] = []
    top_risks: list[dict[str, Any]] = []
    total_exposure = Decimal("0")

    for finding in findings[:10]:
        evidence = finding.evidence if isinstance(finding.evidence, dict) else {}
        dept = str(evidence.get("department_ar") or "").strip()
        supplier = str(evidence.get("supplier_ar") or "").strip()
        if dept and dept != "—" and dept not in departments:
            departments.append(dept)
        if supplier and supplier != "—" and supplier not in suppliers:
            suppliers.append(supplier)
        raw_exposure = evidence.get("amount_exposed_sar")
        exposure_label = str(evidence.get("amount_exposed_label") or "")
        if raw_exposure is not None:
            try:
                total_exposure += Decimal(str(raw_exposure))
            except Exception:
                pass
        top_risks.append(
            {
                "title": sanitize_executive_text(finding.name),
                "description": sanitize_executive_text(finding.description),
                "priority": risk_priority_ar(finding.priority),
                "category": risk_category_ar(finding.category_code),
                "department": dept or "—",
                "supplier": supplier or "—",
                "exposure": exposure_label or "—",
                "score": finding.score,
            }
        )

    rec_titles: list[str] = []
    if recommendation_repository is not None:
        for rec in recommendation_repository.list_for_analysis_run(risk_analysis_run_id)[:8]:
            title = sanitize_executive_text(rec.title.strip())
            if title:
                rec_titles.append(title)

    exposure_phrase = ""
    if total_exposure > 0:
        from app.business.engines.risk.rules.ar import format_sar

        exposure_phrase = f"إجمالي التعرّض المالي المقدّر {format_sar(float(total_exposure))}."

    narrative = (
        f"تحليل المخاطر يُظهر وضعاً {posture} — {total} مخاطر "
        f"({high} عالية الأولوية). {exposure_phrase}"
    ).strip()

    meta = run.runtime_metadata or {}
    ai_summary = meta.get("ai_insights", {})
    if isinstance(ai_summary, dict):
        exec_sum = ai_summary.get("risk_executive_summary")
        if isinstance(exec_sum, str) and exec_sum.strip():
            narrative = sanitize_executive_text(exec_sum.strip())

    return SimulationRiskContext(
        analysis_run_id=str(risk_analysis_run_id),
        posture_ar=posture,
        total_findings=total,
        high_priority_count=high,
        narrative_summary=narrative,
        top_risks=tuple(top_risks),
        recommendations=tuple(rec_titles),
        departments_exposed=tuple(departments),
        suppliers_exposed=tuple(suppliers),
    )
