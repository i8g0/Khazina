/** Executive-facing copy — board-ready financial intelligence language. */

export const EXECUTIVE_MESSAGES = {
  dashboardKpiEmpty:
    "ستظهر المؤشرات التنفيذية بعد إكمال تحليل مالي واحد على الأقل.",
  dashboardKpiSection:
    "ملخص تنفيذي — يُحدَّث بعد اكتمال التحليلات المالية.",
  dashboardKpiHint: "بانتظار التحليل المالي",
  chartDepartmentEmpty:
    "سيظهر توزيع الهدر حسب الإدارة بعد إكمال تحليلات مالية كافية.",
  chartTrendEmpty:
    "سيظهر اتجاه الهدر الزمني بعد إكمال تحليلات مالية كافية.",
  aiUnavailable:
    "خدمة التوصيات الذكية غير متاحة حالياً. أعد المحاولة بعد قليل أو تواصل مع فريق الدعم.",
  aiHealthCheckFailed:
    "تعذّر التحقق من جاهزية خدمة التوصيات. أعد المحاولة بعد قليل.",
  uploadPrimaryHint:
    "ابدأ برفع بياناتك المالية لإطلاق التحليل.",
  uploadQuickHint:
    "رفع مباشر: يرفع الملف ويبدأ التحليل فوراً دون المرور بمركز البيانات.",
  dataUploadNext: "التالي: كشف الهدر",
  simulationDemoHint:
    "صف السيناريو الذي تريد اختباره — سنحسب أثره المالي ونعرض النتائج.",
  usersApiLimit:
    "لا يمكن إضافة مستخدمين أو إعادة تفعيلهم من هنا — يمكنك تعطيل الحسابات فقط.",
} as const;

export function humanizeErrorMessage(message: string): string {
  const trimmed = message.trim();
  if (!trimmed) {
    return "حدث خطأ غير متوقع. حاول مجدداً.";
  }

  const lower = trimmed.toLowerCase();

  if (
    lower.includes("failed to fetch") ||
    lower.includes("networkerror") ||
    lower.includes("network request failed")
  ) {
    return "تعذّر الاتصال بالمنصة. تحقق من الشبكة وحاول مجدداً.";
  }

  if (lower.includes("timeout") || lower.includes("timed out")) {
    return "استغرقت العملية وقتاً أطول من المتوقع. قد تكون ما زالت جارية — أعد المحاولة بعد قليل.";
  }

  if (
    lower.includes("ollama") ||
    lower.includes("qwen") ||
    lower.includes("openai") ||
    lower.includes("model")
  ) {
    return EXECUTIVE_MESSAGES.aiUnavailable;
  }

  if (lower.includes("503") || lower.includes("service unavailable")) {
    return "الخدمة غير متاحة مؤقتاً. أعد المحاولة بعد قليل.";
  }

  if (
    lower.includes("database") ||
    lower.includes("postgres") ||
    lower.includes("sqlalchemy") ||
    lower.includes("sql")
  ) {
    return "تعذّر الوصول إلى بياناتك. أعد المحاولة بعد قليل.";
  }

  if (lower.includes("internal server error")) {
    return "تعذّر إتمام العملية. أعد المحاولة بعد قليل.";
  }

  if (lower.includes("validation error") || lower.includes("validation failed")) {
    return "يرجى مراجعة البيانات المدخلة وإكمال الحقول المطلوبة.";
  }

  if (lower.includes("forbidden") || lower.includes("403")) {
    return "ليس لديك صلاحية لتنفيذ هذا الإجراء.";
  }

  if (lower.includes("not found") || lower.includes("404")) {
    return "البيانات المطلوبة غير متوفرة.";
  }

  if (/\bapi\b/i.test(trimmed) || lower.includes(" aggregation")) {
    return trimmed
      .replace(/\bAPI\b/gi, "المنصة")
      .replace(/تجميع/g, "تحليل")
      .replace(/aggregation/gi, "تحليل");
  }

  return trimmed
    .replace(/\bJSON\b/gi, "")
    .replace(/\bUUID\b/gi, "")
    .replace(/\bsnapshot\b/gi, "البيانات المالية")
    .replace(/\banalysis_run\b/gi, "التحليل")
    .replace(/\bmetadata\b/gi, "")
    .replace(/\bSprint\s*\d+\b/gi, "")
    .replace(/\s{2,}/g, " ")
    .trim();
}
