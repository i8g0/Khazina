"""Per-category risk detection rules — deterministic, no LLM."""

from __future__ import annotations

from decimal import Decimal

from app.business.engines.risk.calculator import RiskCalculationResult
from app.business.engines.risk.constants import (
    CATEGORY_BUDGET,
    CATEGORY_COMPLIANCE,
    CATEGORY_FINANCIAL,
    CATEGORY_FORECAST,
    CATEGORY_FRAUD,
    CATEGORY_LIQUIDITY,
    CATEGORY_OPERATIONAL,
    CATEGORY_STRATEGIC,
    CATEGORY_VENDOR,
)
from app.business.engines.risk.findings import CandidateFinding
from app.business.engines.risk.input import RiskEngineInput
from app.db.models.enums import RiskLevel


def _candidate(
    *,
    category_code: str,
    name: str,
    description: str,
    likelihood: str,
    impact: str,
    rule_id: str,
    evidence: dict,
) -> CandidateFinding:
    return CandidateFinding(
        category_code=category_code,
        name=name,
        description=description,
        likelihood=likelihood,
        impact=impact,
        detection_rule_id=rule_id,
        evidence=evidence,
    )


def detect_financial(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    findings: list[CandidateFinding] = []
    if calc.waste_percentage >= Decimal("10.00"):
        findings.append(
            _candidate(
                category_code=CATEGORY_FINANCIAL,
                name="Elevated financial waste exposure",
                description=(
                    "Financial waste exceeds 10% of total spend, indicating material "
                    "financial stress on the executive baseline."
                ),
                likelihood=RiskLevel.MEDIUM,
                impact=RiskLevel.HIGH,
                rule_id="financial.waste_pct_high",
                evidence={
                    "waste_percentage": str(calc.waste_percentage),
                    "threshold": "10.00",
                },
            )
        )
    elif calc.waste_percentage >= Decimal("5.00"):
        findings.append(
            _candidate(
                category_code=CATEGORY_FINANCIAL,
                name="Moderate financial waste exposure",
                description=(
                    "Financial waste between 5% and 10% of total spend requires "
                    "executive monitoring."
                ),
                likelihood=RiskLevel.LOW,
                impact=RiskLevel.MEDIUM,
                rule_id="financial.waste_pct_medium",
                evidence={
                    "waste_percentage": str(calc.waste_percentage),
                    "threshold_low": "5.00",
                    "threshold_high": "10.00",
                },
            )
        )
    return tuple(findings)


def detect_liquidity(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if calc.liquidity_ratio is None:
        return ()
    ratio = calc.liquidity_ratio
    if ratio < Decimal("1.00"):
        return (
            _candidate(
                category_code=CATEGORY_LIQUIDITY,
                name="Liquidity coverage below threshold",
                description=(
                    "Liquidity coverage ratio is below 1.0, indicating potential "
                    "short-term payment capacity risk."
                ),
                likelihood=RiskLevel.HIGH,
                impact=RiskLevel.HIGH,
                rule_id="liquidity.ratio_critical",
                evidence={"liquidity_ratio": str(ratio), "threshold": "1.00"},
            ),
        )
    if ratio < Decimal("1.50"):
        return (
            _candidate(
                category_code=CATEGORY_LIQUIDITY,
                name="Constrained liquidity coverage",
                description=(
                    "Liquidity coverage ratio is below 1.5, requiring closer cash "
                    "management oversight."
                ),
                likelihood=RiskLevel.MEDIUM,
                impact=RiskLevel.MEDIUM,
                rule_id="liquidity.ratio_elevated",
                evidence={"liquidity_ratio": str(ratio), "threshold": "1.50"},
            ),
        )
    return ()


def detect_operational(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if calc.category_count >= 4:
        return (
            _candidate(
                category_code=CATEGORY_OPERATIONAL,
                name="Distributed operational waste pattern",
                description=(
                    "Waste is spread across four or more categories, suggesting "
                    "operational control gaps in multiple departments."
                ),
                likelihood=RiskLevel.MEDIUM,
                impact=RiskLevel.MEDIUM,
                rule_id="operational.multi_category_waste",
                evidence={"category_count": calc.category_count, "threshold": 4},
            ),
        )
    return ()


def detect_compliance(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if calc.waste_percentage >= Decimal("8.00"):
        return (
            _candidate(
                category_code=CATEGORY_COMPLIANCE,
                name="Compliance oversight threshold exceeded",
                description=(
                    "Waste percentage exceeds the 8% compliance monitoring "
                    "threshold defined for executive financial governance."
                ),
                likelihood=RiskLevel.MEDIUM,
                impact=RiskLevel.HIGH,
                rule_id="compliance.waste_governance_threshold",
                evidence={"waste_percentage": str(calc.waste_percentage), "threshold": "8.00"},
            ),
        )
    return ()


def detect_vendor(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if (
        calc.top_category_concentration is not None
        and calc.top_category_concentration >= Decimal("35.00")
    ):
        return (
            _candidate(
                category_code=CATEGORY_VENDOR,
                name="Vendor or category concentration risk",
                description=(
                    "A single waste category exceeds 35% of total waste, indicating "
                    "supplier or vendor dependency concentration."
                ),
                likelihood=RiskLevel.MEDIUM,
                impact=RiskLevel.HIGH,
                rule_id="vendor.category_concentration",
                evidence={
                    "top_category": calc.top_category_name,
                    "concentration_percentage": str(calc.top_category_concentration),
                    "threshold": "35.00",
                },
            ),
        )
    return ()


def detect_fraud(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if (
        calc.top_category_concentration is not None
        and calc.top_category_concentration >= Decimal("50.00")
    ):
        return (
            _candidate(
                category_code=CATEGORY_FRAUD,
                name="Spend anomaly concentration flag",
                description=(
                    "Deterministic anomaly rule: one category exceeds 50% of waste "
                    "volume, warranting fraud-pattern review."
                ),
                likelihood=RiskLevel.LOW,
                impact=RiskLevel.HIGH,
                rule_id="fraud.spend_concentration_anomaly",
                evidence={
                    "top_category": calc.top_category_name,
                    "concentration_percentage": str(calc.top_category_concentration),
                    "threshold": "50.00",
                },
            ),
        )
    return ()


def detect_budget(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if calc.budget_variance_percentage is None:
        return ()
    variance = calc.budget_variance_percentage
    if variance > Decimal("10.00"):
        return (
            _candidate(
                category_code=CATEGORY_BUDGET,
                name="Adverse budget variance",
                description=(
                    "Actual spend exceeds budget by more than 10%, indicating "
                    "budget execution risk."
                ),
                likelihood=RiskLevel.MEDIUM,
                impact=RiskLevel.MEDIUM,
                rule_id="budget.variance_adverse",
                evidence={"budget_variance_percentage": str(variance), "threshold": "10.00"},
            ),
        )
    if variance < Decimal("-10.00"):
        return (
            _candidate(
                category_code=CATEGORY_BUDGET,
                name="Material budget underspend",
                description=(
                    "Actual spend is more than 10% below budget, indicating plan "
                    "execution or forecasting risk."
                ),
                likelihood=RiskLevel.LOW,
                impact=RiskLevel.MEDIUM,
                rule_id="budget.variance_underspend",
                evidence={"budget_variance_percentage": str(variance), "threshold": "-10.00"},
            ),
        )
    return ()


def detect_strategic(
    calc: RiskCalculationResult, input_data: RiskEngineInput
) -> tuple[CandidateFinding, ...]:
    summary = input_data.simulation_summary
    if summary is None or summary.variance_percentage is None:
        return ()
    variance = summary.variance_percentage
    if abs(variance) >= Decimal("15.00"):
        return (
            _candidate(
                category_code=CATEGORY_STRATEGIC,
                name="Strategic scenario variance",
                description=(
                    "Latest simulation shows material variance from baseline, "
                    "affecting strategic financial assumptions."
                ),
                likelihood=RiskLevel.MEDIUM,
                impact=RiskLevel.HIGH,
                rule_id="strategic.simulation_variance",
                evidence={"variance_percentage": str(variance), "threshold": "15.00"},
            ),
        )
    return ()


def detect_forecast(
    calc: RiskCalculationResult, input_data: RiskEngineInput
) -> tuple[CandidateFinding, ...]:
    summary = input_data.simulation_summary
    if summary is None or summary.projected_metric is None or summary.baseline_metric is None:
        return ()
    if summary.baseline_metric <= 0:
        return ()
    drift = (
        (summary.projected_metric - summary.baseline_metric) / summary.baseline_metric
    ) * Decimal("100")
    if abs(drift) >= Decimal("20.00"):
        return (
            _candidate(
                category_code=CATEGORY_FORECAST,
                name="Forecast projection drift",
                description=(
                    "Projected metrics diverge from baseline by 20% or more, "
                    "signalling forecast reliability risk."
                ),
                likelihood=RiskLevel.MEDIUM,
                impact=RiskLevel.MEDIUM,
                rule_id="forecast.projection_drift",
                evidence={"drift_percentage": str(drift.quantize(Decimal("0.01")))},
            ),
        )
    return ()


CATEGORY_DETECTORS: dict[str, object] = {
    CATEGORY_FINANCIAL: detect_financial,
    CATEGORY_LIQUIDITY: detect_liquidity,
    CATEGORY_OPERATIONAL: detect_operational,
    CATEGORY_COMPLIANCE: detect_compliance,
    CATEGORY_VENDOR: detect_vendor,
    CATEGORY_FRAUD: detect_fraud,
    CATEGORY_BUDGET: detect_budget,
    CATEGORY_STRATEGIC: detect_strategic,
    CATEGORY_FORECAST: detect_forecast,
}
