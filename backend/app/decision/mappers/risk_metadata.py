"""Serialize Risk Engine output for AnalysisRun runtime metadata (Sprint 9.2).

Gold persistence to ``risk_analysis_results`` / ``risk_findings`` is handled
by ``RiskAnalysisService`` + ``RiskGoldMapper`` (Sprint 9.3). Findings are
NOT promoted to the risk register automatically.
"""

from __future__ import annotations

from typing import Any

from app.business.engines.risk.output import RiskEngineOutput


class RiskMetadataMapper:
    @staticmethod
    def to_success_metadata(output: RiskEngineOutput) -> dict[str, Any]:
        calc = output.calculation
        detection = output.detection
        return {
            "risk_analysis": {
                "total_findings": len(output.findings),
                "high_priority_count": detection.high_count,
                "medium_priority_count": detection.medium_count,
                "low_priority_count": detection.low_count,
                "overall_posture_level": detection.overall_posture_level,
                "top_category_code": (
                    output.findings[0].category_code if output.findings else None
                ),
                "liquidity_ratio": (
                    str(calc.liquidity_ratio) if calc.liquidity_ratio is not None else None
                ),
                "waste_percentage": str(calc.waste_percentage),
            },
            "risk_findings": output.findings_to_dicts(),
        }
