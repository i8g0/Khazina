"""Risk Fact Assembler — maps calculator and detector outputs to Facts Contract."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime

from app.business.engines.risk.calculator import RiskCalculationResult
from app.business.engines.risk.detector import RiskDetectionResult
from app.business.engines.risk.manifest import (
    ENGINE_ID,
    ENGINE_VERSION,
    FACTS_CONTRACT_VERSION,
    RISK_ENGINE_MANIFEST,
)
from app.business.facts.contract import Fact, FactsContract


class RiskFactAssembler:
    """Deterministic mapping only — no calculations or natural language generation."""

    def assemble(
        self,
        calculation: RiskCalculationResult,
        detection: RiskDetectionResult,
    ) -> FactsContract:
        timestamp = calculation.generated_at or datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        source = f"{ENGINE_ID}:{calculation.source_dataset}"
        org_id = calculation.organization_id
        period = calculation.reporting_period
        facts: list[Fact] = []

        facts.append(
            Fact(
                domain="risk",
                metric="risk.total_findings",
                value=str(len(detection.findings)),
                unit="count",
                source=source,
                organization_id=org_id,
                period=period,
            )
        )
        facts.append(
            Fact(
                domain="risk",
                metric="risk.high_priority_count",
                value=str(detection.high_count),
                unit="count",
                source=source,
                organization_id=org_id,
                period=period,
            )
        )
        facts.append(
            Fact(
                domain="risk",
                metric="risk.medium_priority_count",
                value=str(detection.medium_count),
                unit="count",
                source=source,
                organization_id=org_id,
                period=period,
            )
        )
        facts.append(
            Fact(
                domain="risk",
                metric="risk.low_priority_count",
                value=str(detection.low_count),
                unit="count",
                source=source,
                organization_id=org_id,
                period=period,
            )
        )
        facts.append(
            Fact(
                domain="risk",
                metric="risk.overall_posture_level",
                value=detection.overall_posture_level,
                severity=detection.overall_posture_level,
                source=source,
                organization_id=org_id,
                period=period,
            )
        )
        facts.append(
            Fact(
                domain="risk",
                metric="risk.waste_percentage",
                value=str(calculation.waste_percentage),
                unit="percent",
                source=source,
                organization_id=org_id,
                period=period,
            )
        )
        facts.append(
            Fact(
                domain="risk",
                metric="risk.category_count",
                value=str(calculation.category_count),
                unit="count",
                source=source,
                organization_id=org_id,
                period=period,
            )
        )

        if calculation.liquidity_ratio is not None:
            facts.append(
                Fact(
                    domain="risk",
                    metric="risk.liquidity_ratio",
                    value=str(calculation.liquidity_ratio),
                    unit="ratio",
                    source=source,
                    organization_id=org_id,
                    period=period,
                )
            )

        if detection.findings:
            max_score = max(item.score for item in detection.findings)
            facts.append(
                Fact(
                    domain="risk",
                    metric="risk.score_max",
                    value=str(max_score),
                    unit="score",
                    source=source,
                    organization_id=org_id,
                    period=period,
                )
            )
            category_counts = Counter(item.category_code for item in detection.findings)
            top_category = max(category_counts.items(), key=lambda pair: pair[1])[0]
            facts.append(
                Fact(
                    domain="risk",
                    metric="risk.top_category",
                    value=top_category,
                    source=source,
                    organization_id=org_id,
                    period=period,
                )
            )
            for finding in detection.findings:
                facts.append(
                    Fact(
                        domain="risk",
                        metric=f"risk.finding.{finding.finding_id}.score",
                        value=str(finding.score),
                        unit="score",
                        severity=finding.priority,
                        source=source,
                        organization_id=org_id,
                        period=period,
                        metadata={
                            "category_code": finding.category_code,
                            "detection_rule_id": finding.detection_rule_id,
                        },
                    )
                )
            for code, count in sorted(category_counts.items()):
                facts.append(
                    Fact(
                        domain="risk",
                        metric=f"risk.category_count.{code}",
                        value=str(count),
                        unit="count",
                        source=source,
                        organization_id=org_id,
                        period=period,
                    )
                )

        return FactsContract(
            contract_version=FACTS_CONTRACT_VERSION,
            engine_id=ENGINE_ID,
            engine_version=ENGINE_VERSION,
            generated_at=timestamp,
            facts=tuple(facts),
            extensions={
                "engine_name": RISK_ENGINE_MANIFEST.engine_name,
                "supported_facts": list(RISK_ENGINE_MANIFEST.supported_facts),
            },
        )
