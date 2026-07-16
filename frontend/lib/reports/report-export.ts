import type { DemoArtifacts } from "@/lib/demo/state";

export const REPORT_TITLES = {
  waste: "تقرير تنفيذي — كشف الهدر",
  risk: "تقرير تنفيذي — المخاطر المالية",
  simulation: "تقرير تنفيذي — محاكاة السيناريو",
} as const;

export interface ReportExportCandidate {
  id: string;
  analysisRunId: string | null;
  hasContent: boolean;
}

/**
 * Resolve which report ID to export — prefers explicit selection, then the report
 * just generated, then the report tied to the active workflow run IDs.
 */
export function resolveExportReportId(
  reports: ReportExportCandidate[],
  artifacts: DemoArtifacts,
  selectedReportId: string | null,
): string | null {
  if (
    selectedReportId &&
    reports.some((row) => row.id === selectedReportId && row.hasContent)
  ) {
    return selectedReportId;
  }

  if (
    artifacts.lastReportId &&
    reports.some((row) => row.id === artifacts.lastReportId && row.hasContent)
  ) {
    return artifacts.lastReportId;
  }

  const activeRunIds = [
    artifacts.riskRunId,
    artifacts.wasteRunId,
    artifacts.simulationAnalysisRunId,
  ].filter((id): id is string => Boolean(id));

  for (const runId of activeRunIds) {
    const match = reports.find(
      (row) => row.analysisRunId === runId && row.hasContent,
    );
    if (match) return match.id;
  }

  const withContent = reports.filter((row) => row.hasContent);
  return withContent[0]?.id ?? null;
}

export function canExportPdf(
  reports: ReportExportCandidate[],
  artifacts: DemoArtifacts,
  selectedReportId: string | null,
): boolean {
  return resolveExportReportId(reports, artifacts, selectedReportId) !== null;
}
