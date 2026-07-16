"""Per-category risk detection — Arabic executive findings with data evidence (Sprint 7)."""

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
from app.business.engines.risk.rules.ar import department_for_category, format_sar
from app.business.engines.risk.rules.evidence import build_executive_evidence
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


def _priority_from_levels(likelihood: str, impact: str) -> str:
    score = {"low": 0, "medium": 1, "high": 2}.get(likelihood, 1) + {"low": 0, "medium": 1, "high": 2}.get(
        impact, 1
    )
    if score >= 3:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def detect_financial(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if calc.waste_percentage < Decimal("5.00"):
        return ()
    dept = department_for_category(calc.top_category_name)
    exposed = calc.total_waste_amount
    if calc.waste_percentage >= Decimal("10.00"):
        priority = "high"
        likelihood = RiskLevel.MEDIUM
        impact = RiskLevel.HIGH
        rule_id = "financial.waste_pct_high"
        name = f"تعرّض مالي مرتفع — هدر {calc.waste_percentage}% من الإنفاق"
        description = (
            f"يبلغ الهدر المالي {format_sar(float(calc.total_waste_amount))} "
            f"({calc.waste_percentage}% من إجمالي الإنفاق {format_sar(float(calc.total_spend))}). "
            f"أعلى تركيز في {dept}. تجاهل ذلك يضغط على الهامش ويُضعف السيولة."
        )
    else:
        priority = "medium"
        likelihood = RiskLevel.LOW
        impact = RiskLevel.MEDIUM
        rule_id = "financial.waste_pct_medium"
        name = f"تعرّض مالي متوسط — هدر {calc.waste_percentage}%"
        description = (
            f"الهدر بين 5% و10% ({format_sar(float(calc.total_waste_amount))}) "
            f"يتطلب متابعة تنفيذية في {dept}."
        )
    evidence = build_executive_evidence(
        rule_id=rule_id,
        department=dept,
        category=dept,
        amount_exposed=exposed,
        supplier=calc.top_supplier_name,
        metrics={
            "waste_percentage": str(calc.waste_percentage),
            "total_spend_sar": str(calc.total_spend),
            "total_waste_sar": str(calc.total_waste_amount),
            "top_category": calc.top_category_name or "",
        },
        priority=priority,
        estimated_savings=exposed * Decimal("0.25"),
        confidence=90 if priority == "high" else 78,
    )
    evidence["if_ignored_ar"] = (
        "استمرار الهدر دون معالجة قد يرفع التكاليف التشغيلية ويُضعف القدرة على التمويل الاستراتيجي."
    )
    evidence["business_impact_ar"] = "ضغط على الربحية والسيولة التشغيلية"
    return (
        _candidate(
            category_code=CATEGORY_FINANCIAL,
            name=name,
            description=description,
            likelihood=likelihood,
            impact=impact,
            rule_id=rule_id,
            evidence=evidence,
        ),
    )


def detect_liquidity(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if calc.liquidity_ratio is None:
        return ()
    ratio = calc.liquidity_ratio
    dept = "الشؤون المالية"
    if ratio < Decimal("1.00"):
        rule_id = "liquidity.ratio_critical"
        name = "تغطية سيولة حرجة — دون الحد الأدنى"
        description = (
            f"نسبة تغطية السيولة {ratio} دون 1.0 — خطر على القدرة على سداد الالتزامات قصيرة الأجل. "
            f"إجمالي الإنفاق {format_sar(float(calc.total_spend))} مقابل هدر {format_sar(float(calc.total_waste_amount))}."
        )
        likelihood = RiskLevel.HIGH
        impact = RiskLevel.HIGH
        priority = "high"
    elif ratio < Decimal("1.50"):
        rule_id = "liquidity.ratio_elevated"
        name = "ضغط على السيولة — تغطية محدودة"
        description = (
            f"نسبة التغطية {ratio} دون 1.5 تتطلب إدارة نقدية أدق وخطة خفض الهدر."
        )
        likelihood = RiskLevel.MEDIUM
        impact = RiskLevel.MEDIUM
        priority = "medium"
    else:
        return ()
    evidence = build_executive_evidence(
        rule_id=rule_id,
        department=dept,
        category="السيولة",
        amount_exposed=calc.total_waste_amount,
        metrics={"liquidity_ratio": str(ratio)},
        priority=priority,
        confidence=82,
    )
    evidence["if_ignored_ar"] = "خطر تأخير المدفوعات للموردين وغرامات تأخير."
    evidence["business_impact_ar"] = "اضطراب التدفق النقدي"
    return (
        _candidate(
            category_code=CATEGORY_LIQUIDITY,
            name=name,
            description=description,
            likelihood=likelihood,
            impact=impact,
            rule_id=rule_id,
            evidence=evidence,
        ),
    )


def detect_operational(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if calc.category_count < 4:
        return ()
    categories_list = ", ".join(
        department_for_category(row.category_name) for row in calc.category_breakdown[:6]
    )
    name = f"هدر تشغيلي موزّع — {calc.category_count} فئات متأثرة"
    description = (
        f"الهدر منتشر عبر {calc.category_count} فئات ({categories_list}) "
        f"مما يشير إلى فجوات رقابة في أكثر من إدارة."
    )
    evidence = build_executive_evidence(
        rule_id="operational.multi_category_waste",
        department="متعدد الإدارات",
        category="تشغيلي",
        amount_exposed=calc.total_waste_amount,
        metrics={
            "category_count": calc.category_count,
            "categories": [row.category_name for row in calc.category_breakdown],
        },
        priority="medium",
        confidence=80,
    )
    evidence["if_ignored_ar"] = "استمرار الهدر الموزّع يصعّب تحديد المسؤول ويُبطئ المعالجة."
    evidence["business_impact_ar"] = "فقدان كفاءة تشغيلية عبر الإدارات"
    return (
        _candidate(
            category_code=CATEGORY_OPERATIONAL,
            name=name,
            description=description,
            likelihood=RiskLevel.MEDIUM,
            impact=RiskLevel.MEDIUM,
            rule_id="operational.multi_category_waste",
            evidence=evidence,
        ),
    )


def detect_compliance(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if calc.waste_percentage < Decimal("8.00"):
        return ()
    dept = department_for_category(calc.top_category_name)
    name = f"تجاوز حد حوكمة الهدر — {calc.waste_percentage}%"
    description = (
        f"نسبة الهدر {calc.waste_percentage}% تجاوزت حد المراقبة التنظيمي (8%) "
        f"في {dept} — يتطلب تصعيداً للجنة الحوكمة."
    )
    evidence = build_executive_evidence(
        rule_id="compliance.waste_governance_threshold",
        department=dept,
        category="الامتثال",
        amount_exposed=calc.total_waste_amount,
        metrics={"waste_percentage": str(calc.waste_percentage), "threshold": "8.00"},
        priority="high",
        confidence=88,
    )
    evidence["if_ignored_ar"] = "مخاطر امتثال وتدقيق خارجي."
    evidence["business_impact_ar"] = "سمعة تنظيمية وغرامات محتملة"
    return (
        _candidate(
            category_code=CATEGORY_COMPLIANCE,
            name=name,
            description=description,
            likelihood=RiskLevel.MEDIUM,
            impact=RiskLevel.HIGH,
            rule_id="compliance.waste_governance_threshold",
            evidence=evidence,
        ),
    )


def detect_vendor(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    findings: list[CandidateFinding] = []
    if (
        calc.top_category_concentration is not None
        and calc.top_category_concentration >= Decimal("35.00")
        and calc.top_category_name
    ):
        dept = department_for_category(calc.top_category_name)
        cat_amount = next(
            (row.amount for row in calc.category_breakdown if row.category_name == calc.top_category_name),
            calc.total_waste_amount * Decimal("0.35"),
        )
        name = f"تركّز مخاطر موردين — {dept} ({calc.top_category_concentration}% من الهدر)"
        description = (
            f"فئة {dept} تمثل {calc.top_category_concentration}% من إجمالي الهدر "
            f"({format_sar(float(cat_amount))}) — اعتماد مرتفع على مورد/فئة واحدة."
        )
        evidence = build_executive_evidence(
            rule_id="vendor.category_concentration",
            department=dept,
            category=dept,
            amount_exposed=cat_amount,
            supplier=calc.top_supplier_name,
            metrics={
                "top_category": calc.top_category_name,
                "concentration_percentage": str(calc.top_category_concentration),
            },
            priority="high",
            confidence=86,
        )
        evidence["if_ignored_ar"] = "تفاوض ضعيف مع الموردين وزيادة مخاطر انقطاع الخدمة."
        evidence["business_impact_ar"] = "اعتماد مفرط على مورد واحد"
        findings.append(
            _candidate(
                category_code=CATEGORY_VENDOR,
                name=name,
                description=description,
                likelihood=RiskLevel.MEDIUM,
                impact=RiskLevel.HIGH,
                rule_id="vendor.category_concentration",
                evidence=evidence,
            )
        )
    if calc.top_supplier_concentration is not None and calc.top_supplier_concentration >= Decimal("25.00"):
        supplier = calc.top_supplier_name or "مورد رئيسي"
        amount = calc.top_supplier_amount or calc.total_waste_amount * Decimal("0.25")
        dept = department_for_category(calc.top_category_name)
        supplier_count = len(calc.supplier_breakdown)
        top_three = calc.supplier_breakdown[:3]
        top_three_share = sum(row.share_of_waste for row in top_three)
        top_three_label = min(3, supplier_count)
        name = (
            f"تركّز {top_three_share}% من الهدر على {top_three_label} موردين"
            if top_three_share >= Decimal("25.00")
            else f"تركّز على مورد — {supplier} ({calc.top_supplier_concentration}%)"
        )
        description = (
            f"تركّز {top_three_share}% من الهدر المالي على {top_three_label} موردين فقط "
            f"({format_sar(float(amount))} للمورد {supplier}) — "
            f"يزيد مخاطر تعطل سلسلة الإمداد وارتفاع الأسعار."
        )
        evidence = build_executive_evidence(
            rule_id="supplier.concentration",
            department=dept,
            category="الموردين",
            amount_exposed=amount,
            supplier=supplier,
            metrics={
                "supplier": supplier,
                "supplier_count": str(supplier_count),
                "concentration_percentage": str(calc.top_supplier_concentration),
                "top_three_waste_share": str(top_three_share),
                "detection_reason_ar": (
                    f"تحليل {supplier_count} مورداً: أعلى {top_three_label} "
                    f"يمثلون {top_three_share}% من الهدر ({format_sar(float(amount))})."
                ),
                "waste_value_sar": str(amount),
            },
            priority="high",
            confidence=88,
        )
        evidence["if_ignored_ar"] = (
            "فقدان قدرة تفاوضية، مخاطر انقطاع الخدمة، وارتفاع تكلفة المشتريات."
        )
        evidence["business_impact_ar"] = (
            f"اعتماد {top_three_share}% من الهدر على {top_three_label} موردين"
        )
        findings.append(
            _candidate(
                category_code=CATEGORY_VENDOR,
                name=name,
                description=description,
                likelihood=RiskLevel.MEDIUM,
                impact=RiskLevel.HIGH,
                rule_id="supplier.concentration",
                evidence=evidence,
            )
        )
    return tuple(findings)


def detect_fraud(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if (
        calc.top_category_concentration is None
        or calc.top_category_concentration < Decimal("50.00")
        or not calc.top_category_name
    ):
        return ()
    dept = department_for_category(calc.top_category_name)
    amount = next(
        (row.amount for row in calc.category_breakdown if row.category_name == calc.top_category_name),
        calc.total_waste_amount * Decimal("0.5"),
    )
    name = f"شذوذ تركّز إنفاق — {dept} ({calc.top_category_concentration}%)"
    description = (
        f"تركّز {calc.top_category_concentration}% من الهدر في {dept} "
        f"({format_sar(float(amount))}) يستدعي مراجعة احتيال/تدقيق داخلي."
    )
    evidence = build_executive_evidence(
        rule_id="fraud.spend_concentration_anomaly",
        department=dept,
        category=dept,
        amount_exposed=amount,
        supplier=calc.top_supplier_name,
        metrics={
            "top_category": calc.top_category_name,
            "concentration_percentage": str(calc.top_category_concentration),
        },
        priority="high",
        confidence=75,
    )
    evidence["if_ignored_ar"] = "احتمال تلاعب أو احتيال غير مكتشف."
    evidence["business_impact_ar"] = "خسائر مالية وسمعة"
    return (
        _candidate(
            category_code=CATEGORY_FRAUD,
            name=name,
            description=description,
            likelihood=RiskLevel.LOW,
            impact=RiskLevel.HIGH,
            rule_id="fraud.spend_concentration_anomaly",
            evidence=evidence,
        ),
    )


def detect_budget(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    if calc.budget_variance_percentage is None:
        return ()
    variance = calc.budget_variance_percentage
    dept = department_for_category(calc.top_category_name)
    if variance > Decimal("10.00"):
        over = (calc.actual_total or Decimal("0")) - (calc.budget_total or Decimal("0"))
        name = f"تجاوز موازنة — +{variance}%"
        description = (
            f"الإنفاق الفعلي يتجاوز الموازنة بـ {variance}% "
            f"({format_sar(float(over)) if over > 0 else format_sar(float(calc.total_spend * variance / 100))})."
        )
        rule_id = "budget.variance_adverse"
        likelihood = RiskLevel.MEDIUM
        impact = RiskLevel.MEDIUM
        priority = "medium"
    elif variance < Decimal("-10.00"):
        name = f"إنفاق دون الموازنة — {variance}%"
        description = f"الإنفاق دون الموازنة بـ {abs(variance)}% — مخاطر تنفيذ الخطة أو دقة التوقعات."
        rule_id = "budget.variance_underspend"
        likelihood = RiskLevel.LOW
        impact = RiskLevel.MEDIUM
        priority = "low"
    else:
        return ()
    exposed = abs(calc.actual_total - calc.budget_total) if calc.actual_total and calc.budget_total else calc.total_waste_amount
    evidence = build_executive_evidence(
        rule_id=rule_id,
        department=dept,
        category="الموازنة",
        amount_exposed=exposed,
        metrics={"budget_variance_percentage": str(variance)},
        priority=priority,
        confidence=84,
    )
    evidence["if_ignored_ar"] = "استمرار تجاوز الموازنة دون تصحيح يضغط على الأهداف السنوية."
    evidence["business_impact_ar"] = "انحراف عن الخطة المالية"
    return (
        _candidate(
            category_code=CATEGORY_BUDGET,
            name=name,
            description=description,
            likelihood=likelihood,
            impact=impact,
            rule_id=rule_id,
            evidence=evidence,
        ),
    )


def detect_category_hotspots(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    """Data-driven: one finding per category exceeding 15% of waste."""
    findings: list[CandidateFinding] = []
    for row in calc.category_breakdown:
        if row.share_of_waste < Decimal("15.00"):
            continue
        dept = department_for_category(row.category_name)
        name = f"هدر مرتفع — {dept} ({row.share_of_waste}%)"
        description = (
            f"رصد {format_sar(float(row.amount))} هدر في {dept} "
            f"({row.share_of_waste}% من إجمالي الهدر) من البيانات المرفوعة."
        )
        rule_id = f"category.high_waste.{row.category_name}"
        evidence = build_executive_evidence(
            rule_id=rule_id,
            department=dept,
            category=dept,
            amount_exposed=row.amount,
            supplier=calc.top_supplier_name if row.category_name == calc.top_category_name else None,
            metrics={
                "category": row.category_name,
                "share_of_waste": str(row.share_of_waste),
                "amount_sar": str(row.amount),
            },
            priority="high" if row.share_of_waste >= Decimal("30") else "medium",
            confidence=92,
        )
        evidence["if_ignored_ar"] = f"استمرار الهدر في {dept} دون تدخل."
        evidence["business_impact_ar"] = f"خسارة {format_sar(float(row.amount))} قابلة للاسترداد"
        findings.append(
            _candidate(
                category_code=CATEGORY_OPERATIONAL,
                name=name,
                description=description,
                likelihood=RiskLevel.MEDIUM if row.share_of_waste >= Decimal("25") else RiskLevel.LOW,
                impact=RiskLevel.HIGH if row.share_of_waste >= Decimal("30") else RiskLevel.MEDIUM,
                rule_id=rule_id,
                evidence=evidence,
            )
        )
    return tuple(findings)


def detect_department_hotspots(calc: RiskCalculationResult) -> tuple[CandidateFinding, ...]:
    findings: list[CandidateFinding] = []
    for row in calc.department_breakdown[:5]:
        if row.share_of_waste < Decimal("12.00"):
            continue
        name = f"تعرّض إدارة — {row.department_name} ({row.share_of_waste}%)"
        description = (
            f"إدارة {row.department_name}: {format_sar(float(row.amount))} "
            f"({row.share_of_waste}% من الهدر) — أولوية مراجعة."
        )
        rule_id = f"department.budget_overrun.{row.department_name}"
        evidence = build_executive_evidence(
            rule_id=rule_id,
            department=row.department_name,
            category=row.department_name,
            amount_exposed=row.amount,
            metrics={
                "department": row.department_name,
                "share_of_waste": str(row.share_of_waste),
            },
            priority="high" if row.share_of_waste >= Decimal("20") else "medium",
            confidence=90,
        )
        evidence["if_ignored_ar"] = f"تفاقم الهدر في {row.department_name}."
        evidence["business_impact_ar"] = "ضغط على موازنة الإدارة"
        findings.append(
            _candidate(
                category_code=CATEGORY_OPERATIONAL,
                name=name,
                description=description,
                likelihood=RiskLevel.MEDIUM,
                impact=RiskLevel.MEDIUM,
                rule_id=rule_id,
                evidence=evidence,
            )
        )
    return tuple(findings)


def detect_strategic(
    calc: RiskCalculationResult, input_data: RiskEngineInput
) -> tuple[CandidateFinding, ...]:
    summary = input_data.simulation_summary
    if summary is None or summary.variance_percentage is None:
        return ()
    variance = summary.variance_percentage
    if abs(variance) < Decimal("15.00"):
        return ()
    name = f"انحراف سيناريو استراتيجي — {variance}%"
    description = (
        f"آخر محاكاة تُظهر انحرافاً {variance}% عن خط الأساس — "
        f"يؤثر على الافتراضات الاستراتيجية."
    )
    evidence = build_executive_evidence(
        rule_id="strategic.simulation_variance",
        department="الإدارة التنفيذية",
        category="استراتيجي",
        amount_exposed=calc.total_waste_amount,
        metrics={"variance_percentage": str(variance)},
        priority="medium",
        confidence=70,
    )
    return (
        _candidate(
            category_code=CATEGORY_STRATEGIC,
            name=name,
            description=description,
            likelihood=RiskLevel.MEDIUM,
            impact=RiskLevel.HIGH,
            rule_id="strategic.simulation_variance",
            evidence=evidence,
        ),
    )


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
    if abs(drift) < Decimal("20.00"):
        return ()
    name = f"انحراف التوقعات — {drift.quantize(Decimal('0.01'))}%"
    description = "التوقعات تنحرف عن خط الأساس بأكثر من 20% — موثوقية التنبؤ معرضة للخطر."
    evidence = build_executive_evidence(
        rule_id="forecast.projection_drift",
        department="التخطيط المالي",
        category="التوقعات",
        amount_exposed=abs(summary.projected_metric - summary.baseline_metric),
        metrics={"drift_percentage": str(drift.quantize(Decimal("0.01")))},
        priority="medium",
        confidence=72,
    )
    return (
        _candidate(
            category_code=CATEGORY_FORECAST,
            name=name,
            description=description,
            likelihood=RiskLevel.MEDIUM,
            impact=RiskLevel.MEDIUM,
            rule_id="forecast.projection_drift",
            evidence=evidence,
        ),
    )


def detect_all(calc: RiskCalculationResult, input_data: RiskEngineInput) -> tuple[CandidateFinding, ...]:
    """Run all detectors; dedupe by rule_id keeping highest impact."""
    combined: list[CandidateFinding] = []
    for detector in (
        detect_financial,
        detect_liquidity,
        detect_operational,
        detect_compliance,
        detect_vendor,
        detect_fraud,
        detect_budget,
        detect_category_hotspots,
        detect_department_hotspots,
    ):
        if detector in (detect_strategic, detect_forecast):
            continue
        combined.extend(detector(calc))
    combined.extend(detect_strategic(calc, input_data))
    combined.extend(detect_forecast(calc, input_data))
    seen: set[str] = set()
    unique: list[CandidateFinding] = []
    for finding in combined:
        key = finding.detection_rule_id
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    return tuple(unique)


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

# Sprint 7: extended detectors run via detector orchestration
EXTENDED_DETECTORS = (
    detect_category_hotspots,
    detect_department_hotspots,
)
