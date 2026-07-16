"""Risk Engine structured output."""

from __future__ import annotations

from dataclasses import dataclass

from app.business.engines.risk.calculator import RiskCalculationResult
from app.business.engines.risk.detector import RiskDetectionResult
from app.business.engines.risk.findings import RiskFinding
from app.business.facts.contract import FactsContract


@dataclass(frozen=True, slots=True)
class RiskEngineOutput:
    """Full deterministic output — findings are NOT auto-promoted to the register."""

    facts_contract: FactsContract
    findings: tuple[RiskFinding, ...]
    calculation: RiskCalculationResult
    detection: RiskDetectionResult

    @property
    def overall_posture_level(self) -> str:
        return self.detection.overall_posture_level

    def findings_to_dicts(self) -> list[dict]:
        return [finding.to_dict() for finding in self.findings]
