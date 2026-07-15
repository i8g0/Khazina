import { apiRequest, downloadBinary } from "@/lib/api/client";
import type {
  AnalysisRunResponse,
  ImportRecordResponse,
  NotificationResponse,
  OrganizationResponse,
  RecommendationResponse,
  ReportContentResponse,
  ReportGenerateResponse,
  ReportResponse,
  ScenarioExecuteResponse,
  SimulationChartPointResponse,
  SimulationComparisonMetricResponse,
  SimulationForecastSummaryResponse,
  SimulationScenarioResponse,
  TimelineEventResponse,
  TokenResponse,
  UploadIngestionResponse,
  WasteAiRecommendationsResponse,
  WasteAnalysisResultResponse,
  WasteCategoryBreakdownResponse,
  WasteDecisionExecuteResponse,
  FinancialFileResponse,
} from "@/lib/api/types";

export async function login(
  email: string,
  password: string,
): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getActiveOrganization(
  token: string,
): Promise<OrganizationResponse> {
  return apiRequest<OrganizationResponse>("/organizations/active", { token });
}

export async function uploadFinancialFile(
  orgId: string,
  token: string,
  file: File,
): Promise<UploadIngestionResponse> {
  const form = new FormData();
  form.append("upload", file);
  return apiRequest<UploadIngestionResponse>(
    `/organizations/${orgId}/financial-files/upload`,
    { method: "POST", token, body: form },
  );
}

export async function listFinancialFiles(
  orgId: string,
  token: string,
): Promise<FinancialFileResponse[]> {
  return apiRequest<FinancialFileResponse[]>(
    `/organizations/${orgId}/financial-files`,
    { token },
  );
}

export async function listImportRecords(
  orgId: string,
  token: string,
): Promise<ImportRecordResponse[]> {
  return apiRequest<ImportRecordResponse[]>(
    `/organizations/${orgId}/import-records`,
    { token },
  );
}

export async function executeWasteDecision(
  orgId: string,
  token: string,
  body: {
    title: string;
    source_file_id: string;
    source_snapshot_id?: string;
    snapshot_version?: number;
  },
): Promise<WasteDecisionExecuteResponse> {
  return apiRequest<WasteDecisionExecuteResponse>(
    `/organizations/${orgId}/decisions/waste/execute`,
    { method: "POST", token, body: JSON.stringify(body) },
  );
}

export async function getWasteResult(
  orgId: string,
  token: string,
  runId: string,
): Promise<WasteAnalysisResultResponse> {
  return apiRequest<WasteAnalysisResultResponse>(
    `/organizations/${orgId}/analysis-runs/${runId}/waste/result`,
    { token },
  );
}

export async function listWasteBreakdowns(
  orgId: string,
  token: string,
  runId: string,
): Promise<WasteCategoryBreakdownResponse[]> {
  return apiRequest<WasteCategoryBreakdownResponse[]>(
    `/organizations/${orgId}/analysis-runs/${runId}/waste/category-breakdowns`,
    { token },
  );
}

export async function generateWasteAi(
  orgId: string,
  token: string,
  analysisRunId: string,
): Promise<WasteAiRecommendationsResponse> {
  return apiRequest<WasteAiRecommendationsResponse>(
    `/organizations/${orgId}/ai-recommendations/waste/generate`,
    {
      method: "POST",
      token,
      body: JSON.stringify({ analysis_run_id: analysisRunId, regenerate: false }),
    },
  );
}

export async function listRecommendations(
  orgId: string,
  token: string,
): Promise<RecommendationResponse[]> {
  return apiRequest<RecommendationResponse[]>(
    `/organizations/${orgId}/recommendations`,
    { token },
  );
}

export async function listScenarios(
  orgId: string,
  token: string,
): Promise<SimulationScenarioResponse[]> {
  return apiRequest<SimulationScenarioResponse[]>(
    `/organizations/${orgId}/simulation/scenarios`,
    { token },
  );
}

export async function executeScenario(
  orgId: string,
  token: string,
  scenarioId: string,
  body: {
    source_file_id: string;
    source_snapshot_id?: string;
    snapshot_version?: number;
    baseline_analysis_run_id?: string;
  },
): Promise<ScenarioExecuteResponse> {
  return apiRequest<ScenarioExecuteResponse>(
    `/organizations/${orgId}/simulation/scenarios/${scenarioId}/execute`,
    { method: "POST", token, body: JSON.stringify(body) },
  );
}

export async function getForecastSummary(
  orgId: string,
  token: string,
  runId: string,
): Promise<SimulationForecastSummaryResponse | null> {
  return apiRequest<SimulationForecastSummaryResponse | null>(
    `/organizations/${orgId}/simulation/runs/${runId}/forecast-summary`,
    { token },
  );
}

export async function listChartPoints(
  orgId: string,
  token: string,
  runId: string,
): Promise<SimulationChartPointResponse[]> {
  return apiRequest<SimulationChartPointResponse[]>(
    `/organizations/${orgId}/simulation/runs/${runId}/chart-points`,
    { token },
  );
}

export async function listComparisonMetrics(
  orgId: string,
  token: string,
  runId: string,
): Promise<SimulationComparisonMetricResponse[]> {
  return apiRequest<SimulationComparisonMetricResponse[]>(
    `/organizations/${orgId}/simulation/runs/${runId}/comparison-metrics`,
    { token },
  );
}

export async function listReports(
  orgId: string,
  token: string,
): Promise<ReportResponse[]> {
  return apiRequest<ReportResponse[]>(`/organizations/${orgId}/reports`, {
    token,
  });
}

export async function getReportContent(
  orgId: string,
  token: string,
  reportId: string,
): Promise<ReportContentResponse> {
  return apiRequest<ReportContentResponse>(
    `/organizations/${orgId}/reports/${reportId}/content`,
    { token },
  );
}

export async function generateReport(
  orgId: string,
  token: string,
  analysisRunId: string,
  title?: string,
): Promise<ReportGenerateResponse> {
  return apiRequest<ReportGenerateResponse>(
    `/organizations/${orgId}/reports/generate`,
    {
      method: "POST",
      token,
      body: JSON.stringify({
        analysis_run_id: analysisRunId,
        title: title ?? "تقرير تنفيذي — كشف الهدر",
      }),
    },
  );
}

export async function downloadReportPdf(
  orgId: string,
  token: string,
  reportId: string,
): Promise<Blob> {
  return downloadBinary(
    `/organizations/${orgId}/reports/${reportId}/export?format=pdf`,
    token,
  );
}

export async function listNotifications(
  orgId: string,
  token: string,
): Promise<NotificationResponse[]> {
  return apiRequest<NotificationResponse[]>(
    `/organizations/${orgId}/notifications`,
    { token },
  );
}

export async function getUnreadCount(
  orgId: string,
  token: string,
): Promise<number> {
  const data = await apiRequest<{ unread_count: number }>(
    `/organizations/${orgId}/notifications/unread-count`,
    { token },
  );
  return data.unread_count;
}

export async function markNotificationRead(
  orgId: string,
  token: string,
  notificationId: string,
): Promise<void> {
  await apiRequest<unknown>(
    `/organizations/${orgId}/notifications/${notificationId}/read`,
    { method: "POST", token },
  );
}

export async function listTimeline(
  orgId: string,
  token: string,
): Promise<TimelineEventResponse[]> {
  return apiRequest<TimelineEventResponse[]>(
    `/organizations/${orgId}/timeline/events`,
    { token },
  );
}

export async function listRecentAnalyses(
  orgId: string,
  token: string,
): Promise<AnalysisRunResponse[]> {
  return apiRequest<AnalysisRunResponse[]>(
    `/organizations/${orgId}/analysis-runs/recent-completed`,
    { token },
  );
}
