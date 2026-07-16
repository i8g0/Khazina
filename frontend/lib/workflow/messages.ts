/** Executive-facing copy — no infrastructure or developer terminology. */

export const EXECUTIVE_MESSAGES = {
  dashboardKpiEmpty:
    "ستظهر المؤشرات التنفيذية بعد إكمال تحليل مالي واحد على الأقل.",
  dashboardKpiSection:
    "ملخص تنفيذي — يُحدَّث تلقائياً بعد اكتمال التحليلات المالية.",
  dashboardKpiHint: "بانتظار التحليل المالي",
  chartDepartmentEmpty:
    "سيظهر توزيع الهدر حسب الإدارة بعد إكمال تحليلات مالية كافية.",
  chartTrendEmpty:
    "سيظهر اتجاه الهدر الزمني بعد إكمال تحليلات مالية كافية.",
  aiUnavailable:
    "خدمة الذكاء الاصطناعي غير متاحة حالياً. أعد المحاولة بعد قليل أو تواصل مع مسؤول المنصة.",
  aiHealthCheckFailed:
    "تعذّر التحقق من جاهزية الذكاء الاصطناعي. أعد المحاولة بعد قليل.",
  uploadPrimaryHint:
    "نقطة البداية الموصى بها — ارفع ملفك المالي هنا لبدء مسار التحليل.",
  uploadQuickHint:
    "رفع سريع: للمستخدمين المتقدمين — يرفع الملف ويشغّل التحليل مباشرة دون المرور بالمستودع.",
  dataUploadNext: "التالي: تحليل الهدر",
  simulationDemoHint:
    "للعرض التجريبي: اختر أحد السيناريوهات الجاهزة ثم اضغط «تشغيل السيناريو».",
  usersApiLimit:
    "لا تتوفر دعوة المستخدمين أو إعادة تفعيلهم من هذه الشاشة — التعطيل متاح فقط.",
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
    return "انتهت مهلة الانتظار. قد تكون العملية ما زالت قيد التنفيذ — أعد المحاولة بعد قليل.";
  }

  if (
    lower.includes("ollama") ||
    lower.includes("qwen") ||
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
    lower.includes("sql")
  ) {
    return "تعذّر الوصول إلى بيانات المنصة. أعد المحاولة بعد قليل.";
  }

  if (/\bapi\b/i.test(trimmed) || lower.includes(" aggregation")) {
    return trimmed
      .replace(/\bAPI\b/gi, "المنصة")
      .replace(/تجميع/g, "تحليل")
      .replace(/aggregation/gi, "تحليل");
  }

  return trimmed;
}
