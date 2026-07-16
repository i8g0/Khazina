"""Arabic executive-facing error and status messages (no developer vocabulary)."""

from __future__ import annotations

from app.ai_recommendations.exceptions import AiRecommendationError
from app.decision.exceptions import SnapshotAdapterError
from app.reports.exceptions import ReportBuilderError
from app.scenario.exceptions import ScenarioInterpretationError
from app.services.exceptions import (
    AuthenticationError,
    BusinessRuleViolationError,
    BusinessValidationError,
    DuplicateResourceError,
    InvalidStateError,
    OwnershipViolationError,
    ResourceNotFoundError,
    ServiceError,
)

_AI_ERROR_MESSAGES: dict[str, str] = {
    "invalid_recommendation_count": "تعذّر إعداد التوصيات — العدد المتوقع بين 3 و6 قرارات تنفيذية",
    "missing_recommendation_title": "إحدى التوصيات ناقصة — أعد التوليد",
    "empty_recommendations": "لم تُنتج التوصيات محتوى كافياً — راجع البيانات المالية",
    "evidence_validation_failed": "التوصية لا تستند إلى أرقام موثقة في البيانات",
    "ai_not_configured": "خدمة التوصيات الذكية غير متاحة حالياً",
    "provider_unavailable": "خدمة التوصيات غير متاحة مؤقتاً — أعد المحاولة",
}

_SNAPSHOT_ERROR_MESSAGES: dict[str, str] = {
    "empty_dataset": "الملف المرفوع لا يحتوي على بيانات مالية قابلة للتحليل",
    "invalid_layout": "تنسيق الملف غير مدعوم — استخدم قالب البيانات المعتمد",
    "non_numeric_amount": "يوجد مبالغ غير رقمية في الملف — راجع الأعمدة المالية",
    "missing_required_column": "الملف ينقصه أعمدة مطلوبة — راجع قالب الرفع",
}

_SCENARIO_ERROR_MESSAGES: dict[str, str] = {
    "empty_request": "يرجى كتابة السيناريو الذي تريد اختباره",
    "invalid_interpretation": "تعذّر فهم السيناريو — صِغه بصيغة أوضح",
    "invalid_ai_json": "تعذّر معالجة السيناريو — أعد المحاولة",
    "invalid_explanation": "تعذّر إعداد شرح النتائج — أعد المحاولة",
}

_REPORT_ERROR_MESSAGES: dict[str, str] = {
    "analysis_not_completed": "التحليل لم يكتمل بعد — انتظر اكتماله ثم أعد إنشاء التقرير",
    "missing_waste_gold": "لا توجد نتائج هدر كافية لإعداد التقرير",
    "pdf_disabled": "تصدير PDF غير مفعّل — تواصل مع مسؤول المؤسسة",
}

_SERVICE_ERROR_MESSAGES: dict[type[ServiceError], str] = {
    AuthenticationError: "البريد الإلكتروني أو كلمة المرور غير صحيحة",
    BusinessValidationError: "البيانات المدخلة غير مكتملة أو غير صالحة",
    DuplicateResourceError: "هذا السجل موجود مسبقاً",
    OwnershipViolationError: "ليس لديك صلاحية للوصول إلى هذه البيانات",
    InvalidStateError: "لا يمكن تنفيذ هذا الإجراء في الحالة الحالية",
    BusinessRuleViolationError: "لا يمكن تنفيذ هذا الإجراء على البيانات الحالية",
    ResourceNotFoundError: "البيانات المطلوبة غير موجودة",
}


def executive_message_for_exception(exc: Exception) -> str | None:
    if isinstance(exc, AiRecommendationError):
        return _AI_ERROR_MESSAGES.get(exc.error_code, exc.message)
    if isinstance(exc, SnapshotAdapterError):
        return _SNAPSHOT_ERROR_MESSAGES.get(exc.error_code, exc.message)
    if isinstance(exc, ScenarioInterpretationError):
        return _SCENARIO_ERROR_MESSAGES.get(exc.error_code, exc.message)
    if isinstance(exc, ReportBuilderError):
        return _REPORT_ERROR_MESSAGES.get(exc.code, exc.message)
    if isinstance(exc, ServiceError):
        for exc_type, message in _SERVICE_ERROR_MESSAGES.items():
            if isinstance(exc, exc_type):
                return message
    return None
