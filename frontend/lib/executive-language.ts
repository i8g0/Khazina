/** Executive financial language — maps internal codes to board-readable Arabic. */

const SCENARIO_TYPE_LABELS: Record<string, string> = {
  increase_profit: "رفع الربحية",
  reduce_expense: "خفض المصاريف",
  reduce_budget: "تقليل الميزانية",
  budget_increase: "زيادة الميزانية",
  increase_budget: "زيادة الميزانية",
  reduce_waste: "تقليل الهدر",
  reduce_suppliers: "تحسين تكلفة الموردين",
  branch_closure: "إغلاق فروع",
  close_branches: "إغلاق فروع",
  employee_hiring: "توسع في التوظيف",
  hire_employees: "توسع في التوظيف",
  increase_payroll: "زيادة الرواتب",
  price_increase: "رفع الأسعار",
  increase_prices: "رفع الأسعار",
  reduce_transport: "خفض تكلفة النقل",
  investment: "استثمار تشغيلي",
  operational_change: "تغيير تشغيلي",
  mixed: "سيناريو مركّب",
};

const TECHNICAL_REPLACEMENTS: Array<[RegExp, string]> = [
  [/\bJSON\b/gi, ""],
  [/\bUUID\b/gi, ""],
  [/\bAPI\b/gi, "المنصة"],
  [/\bKPIs?\b/gi, "المؤشرات الرئيسية"],
  [/\bAI\b/gi, ""],
  [/\bLLM\b/gi, ""],
  [/\bsnapshot\b/gi, "البيانات المالية"],
  [/\banalysis_run\b/gi, "التحليل"],
  [/\bmetadata\b/gi, ""],
  [/\bdataset\b/gi, "البيانات"],
  [/\bfacts_contract\b/gi, ""],
  [/\bengine_id\b/gi, ""],
  [/\bSprint\s*\d+\b/gi, ""],
  [/\bInternal Server Error\b/gi, "تعذّر إتمام العملية"],
  [/\bValidation Error\b/gi, "البيانات المدخلة غير مكتملة"],
  [/\bUnexpected Error\b/gi, "حدث خطأ غير متوقع"],
  [/\bForbidden\b/gi, "ليس لديك صلاحية لهذا الإجراء"],
  [/\bAuthentication failed\b/gi, "تعذّر تسجيل الدخول"],
  [/\bInvalid email or password\b/gi, "البريد الإلكتروني أو كلمة المرور غير صحيحة"],
  [/\bRequest failed\b/gi, "تعذّر إتمام الطلب"],
  [/\bValidation failed\b/gi, "يرجى مراجعة البيانات المدخلة"],
  [/\bThe operation violates a data integrity rule\b/gi, "لا يمكن تنفيذ هذا الإجراء على البيانات الحالية"],
  [/\bwaste\.[a-z0-9_.]+/gi, ""],
  [/\brisk\.[a-z0-9_.]+/gi, ""],
  [/\bscenario\.[a-z0-9_.]+/gi, ""],
  [/\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b/g, ""],
];

export function mapScenarioType(type: string): string {
  const key = type.trim().toLowerCase();
  return SCENARIO_TYPE_LABELS[key] ?? "سيناريو مالي";
}

export function stripTechnicalLanguage(text: string): string {
  let cleaned = text.trim();
  if (!cleaned) return cleaned;
  for (const [pattern, replacement] of TECHNICAL_REPLACEMENTS) {
    cleaned = cleaned.replace(pattern, replacement);
  }
  cleaned = cleaned.replace(/\s{2,}/g, " ").trim();
  return cleaned;
}

import { sanitizeExecutiveText } from "@/lib/format";

const FORBIDDEN_VAGUE_WORDS = [
  /\bقد\b/gu,
  /\bربما\b/gu,
  /\bيمكن\b/gu,
  /\bمن الممكن\b/gu,
];

export function ensureExecutiveArabic(text: string): string {
  let cleaned = stripTechnicalLanguage(sanitizeExecutiveText(text));
  for (const pattern of FORBIDDEN_VAGUE_WORDS) {
    cleaned = cleaned.replace(pattern, "");
  }
  cleaned = cleaned.replace(/\s{2,}/g, " ").trim();
  return cleaned || "—";
}

export const EXECUTIVE_LABELS = {
  businessProblem: "المشكلة التجارية",
  evidence: "الأدلة المالية",
  businessImpact: "الأثر على الأعمال",
  decision: "القرار المطلوب",
  priority: "الأولوية",
  expectedSavings: "الوفورات المتوقعة",
  owner: "الجهة المنفّذة",
  timeline: "الإطار الزمني",
  successKpi: "مؤشر النجاح",
  executiveSummary: "الملخص التنفيذي",
  whyPriority: "لماذا هذه الأولوية",
  unavailable: "غير متوفر في البيانات الحالية",
} as const;
