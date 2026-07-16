import type { DemoArtifacts } from "@/lib/demo/state";
import { navRouteMap } from "@/lib/app-nav";

export type PipelineStageId =
  | "upload"
  | "waste"
  | "ai"
  | "simulation"
  | "report";

export interface PipelineStage {
  id: PipelineStageId;
  label: string;
  shortLabel: string;
  href: string;
}

export const PIPELINE_STAGES: PipelineStage[] = [
  {
    id: "upload",
    label: "رفع الملف المالي",
    shortLabel: "الرفع",
    href: navRouteMap.data,
  },
  {
    id: "waste",
    label: "تحليل الهدر",
    shortLabel: "الهدر",
    href: navRouteMap.waste,
  },
  {
    id: "ai",
    label: "توصيات الذكاء الاصطناعي",
    shortLabel: "التوصيات",
    href: navRouteMap.waste,
  },
  {
    id: "simulation",
    label: "محاكاة السيناريو",
    shortLabel: "المحاكاة",
    href: navRouteMap.simulation,
  },
  {
    id: "report",
    label: "التقرير التنفيذي",
    shortLabel: "التقرير",
    href: navRouteMap.reports,
  },
];

export interface PipelineStageStatus {
  id: PipelineStageId;
  completed: boolean;
  current: boolean;
}

export function isStageCompleted(
  stageId: PipelineStageId,
  artifacts: DemoArtifacts,
): boolean {
  switch (stageId) {
    case "upload":
      return Boolean(artifacts.fileId);
    case "waste":
      return Boolean(artifacts.wasteRunId);
    case "ai":
      return Boolean(artifacts.aiRecommendationsReady);
    case "simulation":
      return Boolean(artifacts.simulationRunId);
    case "report":
      return Boolean(artifacts.lastReportId);
    default:
      return false;
  }
}

export function getFirstIncompleteStage(
  artifacts: DemoArtifacts,
): PipelineStageId {
  for (const stage of PIPELINE_STAGES) {
    if (!isStageCompleted(stage.id, artifacts)) {
      return stage.id;
    }
  }
  return "report";
}

export function resolvePipelineStatuses(
  artifacts: DemoArtifacts,
  activeStageId?: PipelineStageId,
): PipelineStageStatus[] {
  const focusStage = activeStageId ?? getFirstIncompleteStage(artifacts);
  const allComplete = PIPELINE_STAGES.every((stage) =>
    isStageCompleted(stage.id, artifacts),
  );

  return PIPELINE_STAGES.map((stage) => ({
    id: stage.id,
    completed: isStageCompleted(stage.id, artifacts),
    current: allComplete
      ? stage.id === "report"
      : stage.id === focusStage,
  }));
}

export function getContinueTarget(
  artifacts: DemoArtifacts,
): { href: string; label: string } | null {
  if (!artifacts.fileId) {
    return null;
  }
  if (!artifacts.wasteRunId) {
    return {
      href: navRouteMap.waste,
      label: "متابعة: تحليل الهدر",
    };
  }
  if (!artifacts.aiRecommendationsReady) {
    return {
      href: navRouteMap.waste,
      label: "متابعة: توصيات الذكاء الاصطناعي",
    };
  }
  if (!artifacts.simulationRunId) {
    return {
      href: navRouteMap.simulation,
      label: "متابعة: محاكاة السيناريو",
    };
  }
  if (!artifacts.lastReportId) {
    return {
      href: navRouteMap.reports,
      label: "متابعة: إنشاء التقرير",
    };
  }
  return {
    href: navRouteMap.reports,
    label: "عرض التقرير التنفيذي",
  };
}

export function hasActiveAnalysis(artifacts: DemoArtifacts): boolean {
  return Boolean(artifacts.fileId);
}

export function isAnalysisComplete(artifacts: DemoArtifacts): boolean {
  return Boolean(artifacts.lastReportId);
}

export const ROUTE_PIPELINE_STAGE: Record<string, PipelineStageId> = {
  [navRouteMap.data]: "upload",
  [navRouteMap.waste]: "waste",
  [navRouteMap.simulation]: "simulation",
  [navRouteMap.reports]: "report",
};
