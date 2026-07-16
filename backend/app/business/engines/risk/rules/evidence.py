"""Executive evidence builder — every finding must cite uploaded data."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.business.engines.risk.rules.ar import (
    PRIORITY_OWNER,
    PRIORITY_TIMELINE,
    department_for_category,
    format_sar,
)


def build_executive_evidence(
    *,
    rule_id: str,
    department: str,
    category: str,
    amount_exposed: Decimal,
    supplier: str | None = None,
    metrics: dict[str, Any],
    priority: str,
    estimated_savings: Decimal | None = None,
    confidence: int = 85,
    data_source: str = "الملف المرفوع",
) -> dict[str, Any]:
    savings = estimated_savings if estimated_savings is not None else amount_exposed * Decimal("0.35")
    owner = PRIORITY_OWNER.get(priority, "الإدارة المالية")
    timeline = PRIORITY_TIMELINE.get(priority, "60 يوماً")
    waste_raw = metrics.get("waste_value_sar")
    waste_label = metrics.get("waste_value_label")
    if waste_label is None and waste_raw is not None:
        try:
            waste_label = format_sar(float(Decimal(str(waste_raw))))
        except Exception:
            waste_label = "—"
    detection_reason = metrics.get("detection_reason_ar") or (
        f"تحليل {data_source}: تجاوز عتبة المخاطر في {department} "
        f"بمبلغ {format_sar(float(amount_exposed))}."
    )
    financial_impact = metrics.get("financial_impact_ar") or (
        f"تعرّض مالي {format_sar(float(amount_exposed))} على {department}"
    )
    business_impact = metrics.get("business_impact_ar") or (
        f"ضغط على {department} وتقليل مرونة الميزانية التشغيلية"
    )
    if_ignored = metrics.get("if_ignored_ar") or (
        f"استمرار التعرّض في {department} دون معالجة يزيد الهدر ويضعف الحوكمة المالية."
    )
    return {
        **metrics,
        "rule_id": rule_id,
        "department_ar": department,
        "affected_category_ar": category,
        "supplier_ar": supplier or "—",
        "amount_exposed_sar": str(amount_exposed.quantize(Decimal("0.01"))),
        "amount_exposed_label": format_sar(float(amount_exposed)),
        "waste_value_sar": str(waste_raw) if waste_raw is not None else str(amount_exposed),
        "waste_value_label": waste_label or format_sar(float(amount_exposed)),
        "estimated_savings_sar": str(savings.quantize(Decimal("0.01"))),
        "estimated_savings_label": format_sar(float(savings)),
        "recommended_action_ar": _recommended_action(rule_id, department),
        "owner_ar": owner,
        "target_timeline_ar": timeline,
        "confidence_score": confidence,
        "data_source_ar": data_source,
        "detection_reason_ar": detection_reason,
        "financial_impact_ar": financial_impact,
        "business_impact_ar": business_impact,
        "if_ignored_ar": if_ignored,
        "executive_summary_ar": (
            f"{department}: تعرّض {format_sar(float(amount_exposed))} "
            f"— {detection_reason}"
        ),
    }


def _recommended_action(rule_id: str, department: str) -> str:
    actions: dict[str, str] = {
        "financial.waste_pct_high": f"مراجعة فورية لبنود الإنفاق في {department} وخطة خفض الهدر خلال 30 يوماً",
        "financial.waste_pct_medium": f"تفعيل مراقبة شهرية للهدر في {department}",
        "vendor.category_concentration": f"إعادة التفاوض مع الموردين وتنويع مصادر {department}",
        "fraud.spend_concentration_anomaly": f"تدقيق معاملات {department} ومراجعة الضوابط الداخلية",
        "budget.variance_adverse": f"تجميد الإنفاق غير الأساسي في {department} حتى تصحيح الموازنة",
        "operational.multi_category_waste": "خطة تنسيق بين الإدارات المتأثرة لخفض الهدر الموزّع",
        "compliance.waste_governance_threshold": "رفع تقرير للجنة الحوكمة المالية",
        "liquidity.ratio_critical": "تسريع تحصيل الذمم وتأجيل الإنفاق غير العاجل",
        "category.high_waste": f"مراجعة عقود ومشتريات {department}",
        "supplier.concentration": "تنويع قاعدة الموردين وإعادة تقييم العقود",
        "department.budget_overrun": f"مراجعة موازنة {department} وإيقاف البنود الزائدة",
    }
    return actions.get(rule_id, f"وضع خطة معالجة لـ {department} مع متابعة أسبوعية")
