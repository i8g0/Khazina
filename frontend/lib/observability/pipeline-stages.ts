import type { PipelineTimelineEntry } from "@/lib/api/types";

const STAGE_LABELS: Record<string, string> = {
  upload_started: "بدء الرفع",
  upload_completed: "اكتمال الرفع",
  parsing: "قراءة الملف",
  validation: "التحقق من البيانات",
  snapshot_created: "إنشاء اللقطة",
  waste_analysis_started: "بدء تحليل الهدر",
  waste_analysis_completed: "اكتمال تحليل الهدر",
  ai_started: "بدء التوصيات الذكية",
  ai_completed: "اكتمال التوصيات الذكية",
  simulation_started: "بدء المحاكاة",
  simulation_completed: "اكتمال المحاكاة",
  report_generation: "إنشاء التقرير",
  pdf_export: "تصدير PDF",
  completed: "اكتمال التحليل",
  failed: "فشل التحليل",
};

export function getPipelineStageLabel(stage: string): string {
  return STAGE_LABELS[stage] ?? stage;
}

export function getLatestPipelineEntry(
  timeline: PipelineTimelineEntry[] | undefined | null,
): PipelineTimelineEntry | null {
  if (!timeline?.length) return null;
  return timeline[timeline.length - 1] ?? null;
}

export function getPipelineSummary(
  timeline: PipelineTimelineEntry[] | undefined | null,
): string | null {
  const latest = getLatestPipelineEntry(timeline);
  if (!latest) return null;
  const label = getPipelineStageLabel(latest.stage);
  if (latest.status === "failed") {
    return `${label} — فشل`;
  }
  if (latest.status === "completed") {
    return `${label} — مكتمل`;
  }
  return `${label} — جاري التنفيذ`;
}
