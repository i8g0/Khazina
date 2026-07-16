export function formatCurrency(amount: number): string {
  const abs = Math.abs(amount);
  if (abs >= 1_000_000) {
    return `${(amount / 1_000_000).toFixed(2)}M ر.س`;
  }
  if (abs >= 1_000) {
    return `${(amount / 1_000).toFixed(0)}K ر.س`;
  }
  return `${amount.toLocaleString("ar-SA")} ر.س`;
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatDate(value: string): string {
  try {
    return new Date(value).toLocaleDateString("ar-SA");
  } catch {
    return value;
  }
}

export function mapProcessingStatus(status: string): string {
  const normalized = status.toLowerCase();
  if (normalized.includes("ready")) return "جاهز للتحليل";
  if (normalized.includes("complete")) return "مكتمل";
  if (normalized.includes("fail")) return "فشل";
  if (normalized.includes("process")) return "قيد المعالجة";
  return status;
}

export function mapAnalysisType(type: string): string {
  if (type === "financial_waste") return "كشف الهدر";
  if (type === "simulation") return "محاكاة الأعمال";
  if (type === "risk") return "تقييم المخاطر";
  if (type === "waste") return "كشف الهدر";
  return "تحليل مالي";
}


export function mapSimulationStatus(status: string): string {
  const normalized = status.toLowerCase();
  if (normalized === "completed") return "مكتمل";
  if (normalized === "draft") return "مسودة";
  return status;
}

export function mapReportStatus(status: string): string {
  const normalized = status.toLowerCase();
  if (normalized === "ready") return "جاهز";
  if (normalized === "draft") return "مسودة";
  return status;
}

export function mapReportType(type: string): string {
  if (type === "analysis") return "تحليل";
  if (type === "risk") return "مخاطر";
  if (type === "simulation") return "محاكاة";
  return type;
}

export function mapTimelineType(type: string): string {
  if (type === "alert") return "تنبيه";
  if (type === "analysis") return "تحليل";
  if (type === "review") return "مراجعة";
  if (type === "system") return "نظام";
  if (type === "report") return "تقرير";
  return type;
}

export function mapRunStatus(status: string): string {
  const normalized = status.toLowerCase();
  if (normalized === "completed") return "مكتمل";
  if (normalized === "failed") return "فشل";
  if (normalized === "processing") return "قيد المعالجة";
  return status;
}

export function mapRecommendationPriority(priority: string): string {
  const normalized = priority.trim().toLowerCase();
  if (normalized === "high") return "عالية";
  if (normalized === "medium") return "متوسطة";
  if (normalized === "low") return "منخفضة";
  return "غير محددة";
}

export function mapRiskLevel(level: string): string {
  const normalized = level.trim().toLowerCase();
  if (normalized === "high") return "مرتفع";
  if (normalized === "medium") return "متوسط";
  if (normalized === "low") return "منخفض";
  return "غير محدد";
}

export function mapRiskPriority(priority: string): string {
  return mapRecommendationPriority(priority);
}

export function mapRiskPosture(level: string): string {
  const normalized = level.trim().toLowerCase();
  if (normalized === "elevated" || normalized === "critical") return "مرتفع";
  if (normalized === "moderate") return "متوسط";
  if (normalized === "low") return "منخفض";
  if (normalized === "high") return "مرتفع";
  if (normalized === "medium") return "متوسط";
  return "غير محدد";
}

const RISK_CATEGORY_LABELS: Record<string, string> = {
  financial: "مخاطر مالية",
  liquidity: "مخاطر السيولة",
  operational: "مخاطر تشغيلية",
  compliance: "مخاطر امتثال",
  vendor: "مخاطر الموردين",
  fraud: "مخاطر احتيال",
  strategic: "مخاطر استراتيجية",
  budget: "مخاطر الميزانية",
  forecast: "مخاطر التوقعات",
};

export function mapRiskCategoryCode(code: string | null | undefined): string {
  if (!code) return "غير مصنّف";
  const normalized = code.trim().toLowerCase();
  return RISK_CATEGORY_LABELS[normalized] ?? "غير مصنّف";
}

export function mapRecommendationCategory(category: string | null | undefined): string {
  if (!category) return "—";
  const normalized = category.trim().toLowerCase();
  const labels: Record<string, string> = {
    cost_reduction: "خفض التكلفة",
    governance: "حوكمة",
    procurement: "مشتريات",
    operational: "تشغيل",
    compliance: "امتثال",
    vendor: "موردين",
    financial: "مالية",
    risk: "مخاطر",
  };
  return labels[normalized] ?? mapRiskCategoryCode(normalized);
}

export function mapFindingStatus(status: string): string {
  const normalized = status.trim().toLowerCase();
  if (normalized === "detected") return "مكتشف";
  if (normalized === "under_review") return "قيد المراجعة";
  if (normalized === "reviewed") return "تمت المراجعة";
  if (normalized === "promoted") return "مُضاف إلى سجل المخاطر";
  if (normalized === "dismissed") return "مرفوض";
  return "غير محدد";
}

export function mapLifecycleStatus(status: string | null | undefined): string {
  if (!status) return "—";
  if (status === "accepted") return "مقبول";
  if (status === "monitoring") return "مراقبة";
  if (status === "mitigated") return "مُخفَّف";
  if (status === "resolved") return "محلول";
  if (status === "archived") return "مؤرشف";
  return status;
}

export function mapLegacyRiskStatus(status: string): string {
  if (status === "active") return "نشط";
  if (status === "in_progress") return "قيد المعالجة";
  if (status === "closed") return "مغلق";
  return status;
}

export function mapMitigationPlanStatus(status: string): string {
  if (status === "in_progress") return "قيد التنفيذ";
  if (status === "pending_review") return "قيد المراجعة";
  if (status === "completed") return "مكتمل";
  return status;
}

export function mapRiskSourceType(source: string | null | undefined): string {
  if (source === "engine") return "تحليل المخاطر";
  if (source === "manual") return "يدوي";
  if (source === "import") return "استيراد";
  return source ?? "—";
}

const WASTE_CATEGORY_LABELS: Record<string, string> = {
  overlapping_contracts: "العقود المتداخلة",
  operations: "العمليات",
  finance: "الشؤون المالية",
  procurement: "المشتريات",
  travel: "السفر والانتداب",
  it: "تقنية المعلومات",
  hr: "الموارد البشرية",
  marketing: "التسويق",
  compliance: "الامتثال",
};

const ENGLISH_CATEGORY_PATTERN =
  /\b(finance|hr|marketing|operations|procurement|travel|it|compliance|overlapping_contracts)\b/gi;

export function formatWasteCategoryName(categoryKey: string): string {
  const normalized = categoryKey.trim().toLowerCase();
  return WASTE_CATEGORY_LABELS[normalized] ?? categoryKey.replace(/_/g, " ");
}

const RECOMMENDATION_ACTION_PREFIX = /^الإجراء\s*المقتر[ح]?\s*:\s*/u;
const REFERENCE_FACTS_BLOCK = /الحقائق\s*المرجعية\s*:[\s\S]*/u;
const DOT_NOTATION_KEY = /\b(?:waste|risk|scenario)\.[a-z0-9_.]+\b/gi;
const SNAKE_CASE_TOKEN = /\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b/g;
const FORBIDDEN_LITERALS = [
  "facts_contract",
  "metadata",
  "engine_id",
  "engine_version",
  "tasks_executed",
  "source_snapshot_id",
  "source_context",
];

export function sanitizeExecutiveText(text: string): string {
  if (!text?.trim()) return text;
  let cleaned = text.trim();
  cleaned = cleaned.replace(REFERENCE_FACTS_BLOCK, "");
  cleaned = cleaned.replace(DOT_NOTATION_KEY, "");
  for (const literal of FORBIDDEN_LITERALS) {
    cleaned = cleaned.replace(new RegExp(literal, "gi"), "");
  }
  cleaned = cleaned.replace(SNAKE_CASE_TOKEN, "");
  cleaned = cleaned.replace(ENGLISH_CATEGORY_PATTERN, (match) =>
    formatWasteCategoryName(match),
  );
  cleaned = cleaned.replace(/\s{2,}/g, " ").trim();
  return cleaned;
}

export interface ExecutiveRecommendationDisplay {
  title: string;
  description: string;
  problem?: string;
  evidence?: string;
  why?: string;
  rootCause?: string;
  businessImpact?: string;
  expectedSavings?: string;
  timeline?: string;
  ownerDepartment?: string;
  successKpi?: string;
  executiveAngle?: string;
  priorityRationale?: string;
}

const EXEC_FIELD_PATTERNS: Array<{ key: keyof ExecutiveRecommendationDisplay; pattern: RegExp }> = [
  { key: "problem", pattern: /المشكلة\s*:\s*([\s\S]*?)(?=\n\s*(?:الأدلة|الدليل|السبب|التوصية|الإجراء)|$)/u },
  { key: "evidence", pattern: /(?:الأدلة|الدليل)\s*:\s*([\s\S]*?)(?=\n\s*(?:الأثر|السبب|التوصية|الإجراء)|$)/u },
  { key: "rootCause", pattern: /(?:السبب\s*الجذري|السبب)\s*:\s*([\s\S]*?)(?=\n\s*(?:التوصية|الإجراء|الأثر)|$)/u },
  { key: "why", pattern: /(?:لماذا|المبرر)\s*:\s*([\s\S]*?)(?=\n\s*(?:الأثر|الوفورات|الأولوية|المدة|الإدارة|المسؤول)|$)/u },
  { key: "businessImpact", pattern: /الأثر(?:\s*على\s*الأعمال|\s*التجاري|\s*المالي)?\s*:\s*([\s\S]*?)(?=\n\s*(?:الوفورات|الأولوية|المدة|المسؤول|مؤشر)|$)/u },
  { key: "expectedSavings", pattern: /(?:الوفورات\s*المتوقعة|التوفير\s*المتوقع|الوفورات)\s*:\s*([\s\S]*?)(?=\n\s*(?:الأولوية|المدة|المسؤول|مؤشر)|$)/u },
  { key: "timeline", pattern: /(?:المدة\s*الزمنية|الجدول\s*الزمني|الإطار\s*الزمني)\s*:\s*([\s\S]*?)(?=\n\s*(?:المسؤول|الإدارة|مؤشر)|$)/u },
  { key: "ownerDepartment", pattern: /(?:المسؤول|الإدارة\s*المسؤولة|الجهة\s*المسؤولة)\s*:\s*([\s\S]*?)(?=\n\s*مؤشر|$)/u },
  { key: "successKpi", pattern: /(?:مؤشر\s*النجاح|مؤشر\s*الأداء)\s*:\s*([\s\S]*?)$/u },
];

export function parseExecutiveRecommendation(rec: {
  title: string;
  description: string;
  source_context?: Record<string, unknown> | null;
}): ExecutiveRecommendationDisplay {
  const executive = rec.source_context?.executive as Record<string, string> | undefined;
  if (executive?.recommendation || executive?.action) {
    const recommendation = executive.recommendation || executive.action;
    return {
      title: sanitizeExecutiveText(recommendation),
      description: sanitizeExecutiveText(
        [
          executive.problem && `المشكلة: ${executive.problem}`,
          executive.evidence && `الأدلة: ${executive.evidence}`,
          executive.root_cause && `السبب الجذري: ${executive.root_cause}`,
          executive.business_impact && `الأثر: ${executive.business_impact}`,
          executive.expected_savings && `الوفورات: ${executive.expected_savings}`,
        ]
          .filter(Boolean)
          .join("\n"),
      ),
      problem: sanitizeExecutiveText(executive.problem ?? ""),
      evidence: sanitizeExecutiveText(executive.evidence ?? ""),
      rootCause: sanitizeExecutiveText(executive.root_cause ?? executive.why ?? ""),
      why: sanitizeExecutiveText(executive.why ?? executive.root_cause ?? ""),
      businessImpact: sanitizeExecutiveText(executive.business_impact ?? ""),
      expectedSavings: sanitizeExecutiveText(executive.expected_savings ?? ""),
      timeline: sanitizeExecutiveText(executive.timeline ?? ""),
      ownerDepartment: sanitizeExecutiveText(executive.owner_department ?? ""),
      successKpi: sanitizeExecutiveText(executive.success_kpi ?? ""),
      executiveAngle: sanitizeExecutiveText(executive.executive_angle ?? ""),
      priorityRationale: sanitizeExecutiveText(executive.priority_rationale ?? ""),
    };
  }

  const combined = `${rec.title}\n${rec.description}`;
  const parsed: ExecutiveRecommendationDisplay = formatRecommendationDisplay(rec);
  for (const { key, pattern } of EXEC_FIELD_PATTERNS) {
    const match = combined.match(pattern);
    if (match?.[1]) {
      parsed[key] = sanitizeExecutiveText(match[1].trim());
    }
  }
  if (parsed.evidence || parsed.problem || parsed.why) {
    parsed.description = [
      parsed.problem && `المشكلة: ${parsed.problem}`,
      parsed.evidence && `الأدلة: ${parsed.evidence}`,
      parsed.rootCause && `السبب الجذري: ${parsed.rootCause}`,
      parsed.why && `لماذا: ${parsed.why}`,
      parsed.businessImpact && `الأثر على الأعمال: ${parsed.businessImpact}`,
      parsed.expectedSavings && `الوفورات المتوقعة: ${parsed.expectedSavings}`,
    ]
      .filter(Boolean)
      .join("\n");
  }
  return parsed;
}

export function formatRecommendationDisplay(rec: {
  title: string;
  description: string;
}): { title: string; description: string } {
  const rawTitle = sanitizeExecutiveText(rec.title.trim());
  const description = sanitizeExecutiveText(rec.description.trim());
  let title = rawTitle.replace(RECOMMENDATION_ACTION_PREFIX, "").trim();

  if (!title) {
    title = description.slice(0, 120);
  } else if (title.length > 140) {
    title = `${title.slice(0, 137)}…`;
  }

  const rationaleMatch = description.match(/المبرر\s*:\s*([\s\S]+)/u);
  const displayDescription = rationaleMatch
    ? sanitizeExecutiveText(rationaleMatch[1].trim())
    : description;

  if (displayDescription === rawTitle || displayDescription.startsWith(rawTitle)) {
    return {
      title,
      description:
        displayDescription.slice(title.length).trim() || displayDescription,
    };
  }

  return { title, description: displayDescription || description };
}
