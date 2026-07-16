"""Maps Risk Engine output to Gold persistence payloads (Sprint 9.3)."""

from __future__ import annotations

import uuid
from typing import Any

from app.business.engines.risk.output import RiskEngineOutput


class RiskGoldMapper:
    """Deterministic engine output → ``RiskAnalysisService`` persistence payload."""

    @staticmethod
    def to_persistence_payload(
        output: RiskEngineOutput,
        *,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        source_snapshot_id: uuid.UUID | None,
    ) -> dict[str, Any]:
        detection = output.detection
        facts = output.facts_contract
        top_category_code = (
            output.findings[0].category_code if output.findings else None
        )

        return {
            "result": {
                "analysis_run_id": analysis_run_id,
                "organization_id": organization_id,
                "total_findings": len(output.findings),
                "high_priority_count": detection.high_count,
                "medium_priority_count": detection.medium_count,
                "low_priority_count": detection.low_count,
                "overall_posture_level": detection.overall_posture_level,
                "top_category_code": top_category_code,
                "facts_contract_version": facts.contract_version,
                "source_snapshot_id": source_snapshot_id,
            },
            "findings": [
                RiskGoldMapper._finding_row(
                    finding,
                    organization_id=organization_id,
                    analysis_run_id=analysis_run_id,
                )
                for finding in output.findings
            ],
        }

    @staticmethod
    def _finding_row(
        finding: Any,
        *,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
    ) -> dict[str, Any]:
        return {
            "id": uuid.UUID(finding.finding_id),
            "analysis_run_id": analysis_run_id,
            "organization_id": organization_id,
            "category_code": finding.category_code,
            "name": finding.name,
            "description": finding.description,
            "likelihood": finding.likelihood,
            "impact": finding.impact,
            "score": finding.score,
            "priority": finding.priority,
            "detection_rule_id": finding.detection_rule_id,
            "evidence": dict(finding.evidence),
            "finding_status": finding.finding_status,
            "promoted_risk_id": None,
            "department_id": None,
        }
