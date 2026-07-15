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
  return priority;
}
