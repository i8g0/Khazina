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
  if (type === "financial_waste") return "هدر مالي";
  if (type === "simulation") return "محاكاة";
  if (type === "risk") return "مخاطر";
  return type;
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
  if (priority === "high") return "عالية";
  if (priority === "medium") return "متوسطة";
  if (priority === "low") return "منخفضة";
  return priority;
}

export function mapRiskLevel(level: string): string {
  if (level === "high") return "مرتفع";
  if (level === "medium") return "متوسط";
  if (level === "low") return "منخفض";
  return level;
}

export function mapRiskPriority(priority: string): string {
  return mapRecommendationPriority(priority);
}

export function mapRiskPosture(level: string): string {
  if (level === "elevated") return "مرتفع";
  if (level === "moderate") return "متوسط";
  if (level === "low") return "منخفض";
  return level;
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
  return RISK_CATEGORY_LABELS[code] ?? code.replace(/_/g, " ");
}

export function mapFindingStatus(status: string): string {
  if (status === "detected") return "مكتشف";
  if (status === "under_review") return "قيد المراجعة";
  if (status === "reviewed") return "تمت المراجعة";
  if (status === "promoted") return "مُرقّى للسجل";
  if (status === "dismissed") return "مرفوض";
  return status;
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
  if (source === "engine") return "محرك المخاطر";
  if (source === "manual") return "يدوي";
  if (source === "import") return "استيراد";
  return source ?? "—";
}

const WASTE_CATEGORY_LABELS: Record<string, string> = {
  overlapping_contracts: "العقود المتداخلة",
  operations: "العمليات",
  finance: "الشؤون المالية",
};

export function formatWasteCategoryName(categoryKey: string): string {
  const normalized = categoryKey.trim().toLowerCase();
  return WASTE_CATEGORY_LABELS[normalized] ?? categoryKey.replace(/_/g, " ");
}

const RECOMMENDATION_ACTION_PREFIX = /^الإجراء المقترح:\s*/u;

export function formatRecommendationDisplay(rec: {
  title: string;
  description: string;
}): { title: string; description: string } {
  const rawTitle = rec.title.trim();
  const description = rec.description.trim();
  let title = rawTitle.replace(RECOMMENDATION_ACTION_PREFIX, "").trim();

  if (!title) {
    title = description.slice(0, 120);
  } else if (title.length > 140) {
    title = `${title.slice(0, 137)}…`;
  }

  if (description === rawTitle || description.startsWith(rawTitle)) {
    return { title, description: description.slice(title.length).trim() || description };
  }

  return { title, description };
}
