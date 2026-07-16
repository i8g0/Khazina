import { apiRequest, downloadBinary } from "@/lib/api/client";
import type {
  AnalysisRunResponse,
  DataQualityCheckResponse,
  DataQualitySnapshotResponse,
  DepartmentResponse,
  FinancialFileResponse,
  ImportRecordResponse,
  ListQueryParams,
  NotificationResponse,
  OrganizationResponse,
  RecommendationResponse,
  ReportContentResponse,
  ReportGenerateResponse,
  ReportResponse,
  ReportingPeriodResponse,
  ResolvedSettingsResponse,
  AISimulationExecuteResponse,
  ScenarioExecuteResponse,
  SettingsPatchPayload,
  SimulationChartPointResponse,
  SimulationComparisonMetricResponse,
  SimulationAssumptionResponse,
  SimulationImpactItemResponse,
  SimulationActionItemResponse,
  SimulationForecastSummaryResponse,
  SimulationScenarioResponse,
  TimelineEventResponse,
  TokenResponse,
  UploadIngestionResponse,
  UserNotificationPreferencesResponse,
  UserResponse,
  WasteAiRecommendationsResponse,
  WasteAnalysisResultResponse,
  WasteCategoryBreakdownResponse,
  WasteVendorFindingResponse,
  AiHealthResponse,
  SystemHealthResponse,
  WasteDecisionExecuteResponse,
  RiskAnalysisExecuteResponse,
  RiskAnalysisRunDetailResponse,
  RiskAnalysisResultResponse,
  RiskFindingResponse,
  RiskResponse,
  MitigationPlanResponse,
  RiskEventResponse,
  RiskProvenanceResponse,
  RiskPromotionResponse,
  RiskAiRecommendationsResponse,
} from "@/lib/api/types";

function toQuery(
  params: object,
): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    search.set(key, String(value));
  }
  const serialized = search.toString();
  return serialized ? `?${serialized}` : "";
}

export async function login(
  email: string,
  password: string,
): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getAiHealth(): Promise<AiHealthResponse> {
  return apiRequest<AiHealthResponse>("/ai/health");
}

export async function getSystemHealth(): Promise<SystemHealthResponse> {
  return apiRequest<SystemHealthResponse>("/health");
}

export async function getActiveOrganization(
  token: string,
): Promise<OrganizationResponse> {
  return apiRequest<OrganizationResponse>("/organizations/active", { token });
}

export async function getOrganization(
  orgId: string,
  token: string,
): Promise<OrganizationResponse> {
  return apiRequest<OrganizationResponse>(`/organizations/${orgId}`, { token });
}

export async function patchOrganization(
  orgId: string,
  token: string,
  body: {
    name?: string;
    platform_name?: string;
    executive_title?: string | null;
  },
): Promise<OrganizationResponse> {
  return apiRequest<OrganizationResponse>(`/organizations/${orgId}`, {
    method: "PATCH",
    token,
    body: JSON.stringify(body),
  });
}

export async function listDepartments(
  orgId: string,
  token: string,
  options: ListQueryParams & { active_only?: boolean } = {},
): Promise<DepartmentResponse[]> {
  return apiRequest<DepartmentResponse[]>(
    `/organizations/${orgId}/departments${toQuery(options)}`,
    { token },
  );
}

export async function createDepartment(
  orgId: string,
  token: string,
  body: { name_ar: string; code?: string | null; display_order?: number },
): Promise<DepartmentResponse> {
  return apiRequest<DepartmentResponse>(`/organizations/${orgId}/departments`, {
    method: "POST",
    token,
    body: JSON.stringify(body),
  });
}

export async function patchDepartment(
  orgId: string,
  token: string,
  departmentId: string,
  body: {
    name_ar?: string;
    code?: string | null;
    display_order?: number;
  },
): Promise<DepartmentResponse> {
  return apiRequest<DepartmentResponse>(
    `/organizations/${orgId}/departments/${departmentId}`,
    { method: "PATCH", token, body: JSON.stringify(body) },
  );
}

export async function deactivateDepartment(
  orgId: string,
  token: string,
  departmentId: string,
): Promise<DepartmentResponse> {
  return apiRequest<DepartmentResponse>(
    `/organizations/${orgId}/departments/${departmentId}/deactivate`,
    { method: "POST", token },
  );
}

export async function reactivateDepartment(
  orgId: string,
  token: string,
  departmentId: string,
): Promise<DepartmentResponse> {
  return apiRequest<DepartmentResponse>(
    `/organizations/${orgId}/departments/${departmentId}/reactivate`,
    { method: "POST", token },
  );
}

export async function listReportingPeriods(
  orgId: string,
  token: string,
  options: ListQueryParams = {},
): Promise<ReportingPeriodResponse[]> {
  return apiRequest<ReportingPeriodResponse[]>(
    `/organizations/${orgId}/reporting-periods${toQuery(options)}`,
    { token },
  );
}

export async function createReportingPeriod(
  orgId: string,
  token: string,
  body: {
    label: string;
    start_date?: string | null;
    end_date?: string | null;
    activate?: boolean;
  },
): Promise<ReportingPeriodResponse> {
  return apiRequest<ReportingPeriodResponse>(
    `/organizations/${orgId}/reporting-periods`,
    { method: "POST", token, body: JSON.stringify(body) },
  );
}

export async function activateReportingPeriod(
  orgId: string,
  token: string,
  periodId: string,
): Promise<ReportingPeriodResponse> {
  return apiRequest<ReportingPeriodResponse>(
    `/organizations/${orgId}/reporting-periods/${periodId}/activate`,
    { method: "POST", token },
  );
}

export async function closeActiveReportingPeriod(
  orgId: string,
  token: string,
): Promise<ReportingPeriodResponse> {
  return apiRequest<ReportingPeriodResponse>(
    `/organizations/${orgId}/reporting-periods/close-active`,
    { method: "POST", token },
  );
}

export async function listUsers(
  orgId: string,
  token: string,
  options: ListQueryParams & { active_only?: boolean } = {},
): Promise<UserResponse[]> {
  return apiRequest<UserResponse[]>(
    `/organizations/${orgId}/users${toQuery(options)}`,
    { token },
  );
}

export async function createUser(
  orgId: string,
  token: string,
  body: {
    full_name: string;
    email: string;
    password: string;
    role?: UserResponse["role"];
  },
): Promise<UserResponse> {
  return apiRequest<UserResponse>(`/organizations/${orgId}/users`, {
    method: "POST",
    token,
    body: JSON.stringify(body),
  });
}

export async function patchUser(
  orgId: string,
  token: string,
  userId: string,
  body: {
    full_name?: string;
    email?: string;
    password?: string;
    role?: UserResponse["role"];
  },
): Promise<UserResponse> {
  return apiRequest<UserResponse>(`/organizations/${orgId}/users/${userId}`, {
    method: "PATCH",
    token,
    body: JSON.stringify(body),
  });
}

export async function deactivateUser(
  orgId: string,
  token: string,
  userId: string,
): Promise<UserResponse> {
  return apiRequest<UserResponse>(
    `/organizations/${orgId}/users/${userId}/deactivate`,
    { method: "POST", token },
  );
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
  fileId: string,
): Promise<ImportRecordResponse[]> {
  return apiRequest<ImportRecordResponse[]>(
    `/organizations/${orgId}/financial-files/${fileId}/import-records`,
    { token },
  );
}

export async function getLatestQualitySnapshot(
  orgId: string,
  token: string,
): Promise<DataQualitySnapshotResponse | null> {
  return apiRequest<DataQualitySnapshotResponse | null>(
    `/organizations/${orgId}/data-quality-snapshots/latest`,
    { token, allowNull: true },
  );
}

export async function listQualityChecks(
  orgId: string,
  token: string,
  snapshotId: string,
): Promise<DataQualityCheckResponse[]> {
  return apiRequest<DataQualityCheckResponse[]>(
    `/organizations/${orgId}/data-quality-snapshots/${snapshotId}/checks`,
    { token },
  );
}

export async function getOrganizationSettings(
  orgId: string,
  token: string,
): Promise<ResolvedSettingsResponse> {
  return apiRequest<ResolvedSettingsResponse>(
    `/organizations/${orgId}/settings`,
    { token },
  );
}

export async function patchOrganizationSettings(
  orgId: string,
  token: string,
  body: SettingsPatchPayload,
): Promise<ResolvedSettingsResponse> {
  return apiRequest<ResolvedSettingsResponse>(
    `/organizations/${orgId}/settings`,
    { method: "PATCH", token, body: JSON.stringify(body) },
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

export async function listVendorFindings(
  orgId: string,
  token: string,
  runId: string,
  options: ListQueryParams = {},
): Promise<WasteVendorFindingResponse[]> {
  return apiRequest<WasteVendorFindingResponse[]>(
    `/organizations/${orgId}/analysis-runs/${runId}/waste/vendor-findings${toQuery(options)}`,
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
  options: ListQueryParams & { domain_source?: string; priority?: string } = {},
): Promise<RecommendationResponse[]> {
  return apiRequest<RecommendationResponse[]>(
    `/organizations/${orgId}/recommendations${toQuery(options)}`,
    { token },
  );
}

// -- Risk analysis (Sprint 9.6) ------------------------------------------------

export async function executeRiskAnalysis(
  orgId: string,
  token: string,
  body: {
    title: string;
    source_file_id: string;
    source_snapshot_id?: string;
    snapshot_version?: number;
    reporting_period_id?: string;
  },
): Promise<RiskAnalysisExecuteResponse> {
  return apiRequest<RiskAnalysisExecuteResponse>(
    `/organizations/${orgId}/risk-analyses/execute`,
    { method: "POST", token, body: JSON.stringify(body) },
  );
}

export async function listRiskAnalyses(
  orgId: string,
  token: string,
  options: ListQueryParams & { status?: string } = {},
): Promise<AnalysisRunResponse[]> {
  return apiRequest<AnalysisRunResponse[]>(
    `/organizations/${orgId}/risk-analyses${toQuery(options)}`,
    { token },
  );
}

export async function getRiskAnalysis(
  orgId: string,
  token: string,
  runId: string,
): Promise<RiskAnalysisRunDetailResponse> {
  return apiRequest<RiskAnalysisRunDetailResponse>(
    `/organizations/${orgId}/risk-analyses/${runId}`,
    { token },
  );
}

export async function getRiskResult(
  orgId: string,
  token: string,
  runId: string,
): Promise<RiskAnalysisResultResponse> {
  return apiRequest<RiskAnalysisResultResponse>(
    `/organizations/${orgId}/risk-analyses/${runId}/result`,
    { token },
  );
}

export async function listRiskFindings(
  orgId: string,
  token: string,
  runId: string,
  options: ListQueryParams & {
    priority?: string;
    category_code?: string;
    finding_status?: string;
  } = {},
): Promise<RiskFindingResponse[]> {
  return apiRequest<RiskFindingResponse[]>(
    `/organizations/${orgId}/risk-analyses/${runId}/findings${toQuery(options)}`,
    { token },
  );
}

export async function getRiskFinding(
  orgId: string,
  token: string,
  runId: string,
  findingId: string,
): Promise<RiskFindingResponse> {
  return apiRequest<RiskFindingResponse>(
    `/organizations/${orgId}/risk-analyses/${runId}/findings/${findingId}`,
    { token },
  );
}

export async function generateRiskAi(
  orgId: string,
  token: string,
  analysisRunId: string,
  regenerate = false,
): Promise<RiskAiRecommendationsResponse> {
  return apiRequest<RiskAiRecommendationsResponse>(
    `/organizations/${orgId}/ai-recommendations/risk/generate`,
    {
      method: "POST",
      token,
      body: JSON.stringify({
        analysis_run_id: analysisRunId,
        regenerate,
      }),
    },
  );
}

// -- Risk register & governance ------------------------------------------------

export async function listRisks(
  orgId: string,
  token: string,
  options: ListQueryParams & {
    status?: string;
    lifecycle_status?: string;
    priority?: string;
    department_id?: string;
    category_code?: string;
    source_type?: string;
  } = {},
): Promise<RiskResponse[]> {
  return apiRequest<RiskResponse[]>(
    `/organizations/${orgId}/risks${toQuery(options)}`,
    { token },
  );
}

export async function getRisk(
  orgId: string,
  token: string,
  riskId: string,
): Promise<RiskResponse> {
  return apiRequest<RiskResponse>(`/organizations/${orgId}/risks/${riskId}`, {
    token,
  });
}

export async function reviewRiskFinding(
  orgId: string,
  token: string,
  findingId: string,
  body: { action: string; reason?: string },
): Promise<RiskFindingResponse> {
  return apiRequest<RiskFindingResponse>(
    `/organizations/${orgId}/risk-findings/${findingId}/review`,
    { method: "POST", token, body: JSON.stringify(body) },
  );
}

export async function promoteRiskFinding(
  orgId: string,
  token: string,
  findingId: string,
  body: { owner_label?: string; department_id?: string; reason?: string } = {},
): Promise<RiskPromotionResponse> {
  return apiRequest<RiskPromotionResponse>(
    `/organizations/${orgId}/risk-findings/${findingId}/promote`,
    { method: "POST", token, body: JSON.stringify(body) },
  );
}

export async function updateRiskLifecycleStatus(
  orgId: string,
  token: string,
  riskId: string,
  body: { lifecycle_status: string; reason?: string },
): Promise<RiskResponse> {
  return apiRequest<RiskResponse>(
    `/organizations/${orgId}/risks/${riskId}/status`,
    { method: "PATCH", token, body: JSON.stringify(body) },
  );
}

export async function reviewEnterpriseRisk(
  orgId: string,
  token: string,
  riskId: string,
  body: { action: string; reason?: string },
): Promise<RiskResponse> {
  return apiRequest<RiskResponse>(
    `/organizations/${orgId}/risks/${riskId}/review`,
    { method: "POST", token, body: JSON.stringify(body) },
  );
}

export async function getRiskHistory(
  orgId: string,
  token: string,
  riskId: string,
  options: ListQueryParams = {},
): Promise<RiskEventResponse[]> {
  return apiRequest<RiskEventResponse[]>(
    `/organizations/${orgId}/risks/${riskId}/history${toQuery(options)}`,
    { token },
  );
}

export async function getRiskProvenance(
  orgId: string,
  token: string,
  riskId: string,
): Promise<RiskProvenanceResponse> {
  return apiRequest<RiskProvenanceResponse>(
    `/organizations/${orgId}/risks/${riskId}/provenance`,
    { token },
  );
}

export async function listMitigationPlans(
  orgId: string,
  token: string,
  options: ListQueryParams = {},
): Promise<MitigationPlanResponse[]> {
  return apiRequest<MitigationPlanResponse[]>(
    `/organizations/${orgId}/mitigation-plans${toQuery(options)}`,
    { token },
  );
}

export async function listRiskMitigationPlans(
  orgId: string,
  token: string,
  riskId: string,
): Promise<MitigationPlanResponse[]> {
  return apiRequest<MitigationPlanResponse[]>(
    `/organizations/${orgId}/risks/${riskId}/mitigation-plans`,
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

export async function createScenario(
  orgId: string,
  token: string,
  body: { name: string; description: string },
): Promise<SimulationScenarioResponse> {
  return apiRequest<SimulationScenarioResponse>(
    `/organizations/${orgId}/simulation/scenarios`,
    { method: "POST", token, body: JSON.stringify(body) },
  );
}

export async function executeAISimulation(
  orgId: string,
  token: string,
  body: {
    user_request: string;
    source_file_id: string;
    source_snapshot_id?: string;
    snapshot_version?: number;
    baseline_analysis_run_id?: string;
  },
): Promise<AISimulationExecuteResponse> {
  return apiRequest<AISimulationExecuteResponse>(
    `/organizations/${orgId}/simulation/ai/execute`,
    { method: "POST", token, body: JSON.stringify(body) },
  );
}

export async function getAnalysisRun(
  orgId: string,
  token: string,
  runId: string,
): Promise<AnalysisRunResponse> {
  return apiRequest<AnalysisRunResponse>(
    `/organizations/${orgId}/analysis-runs/${runId}`,
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
    { token, allowNull: true },
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

export async function listScenarioAssumptions(
  orgId: string,
  token: string,
  scenarioId: string,
): Promise<SimulationAssumptionResponse[]> {
  return apiRequest<SimulationAssumptionResponse[]>(
    `/organizations/${orgId}/simulation/scenarios/${scenarioId}/assumptions`,
    { token },
  );
}

export async function listImpactItems(
  orgId: string,
  token: string,
  runId: string,
): Promise<SimulationImpactItemResponse[]> {
  return apiRequest<SimulationImpactItemResponse[]>(
    `/organizations/${orgId}/simulation/runs/${runId}/impact-items`,
    { token },
  );
}

export async function listActionItems(
  orgId: string,
  token: string,
  runId: string,
): Promise<SimulationActionItemResponse[]> {
  return apiRequest<SimulationActionItemResponse[]>(
    `/organizations/${orgId}/simulation/runs/${runId}/action-items`,
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
  title: string,
): Promise<ReportGenerateResponse> {
  return apiRequest<ReportGenerateResponse>(
    `/organizations/${orgId}/reports/generate`,
    {
      method: "POST",
      token,
      body: JSON.stringify({
        analysis_run_id: analysisRunId,
        title,
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
  options: ListQueryParams & { unread_only?: boolean } = {},
): Promise<NotificationResponse[]> {
  return apiRequest<NotificationResponse[]>(
    `/organizations/${orgId}/notifications${toQuery(options)}`,
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
): Promise<NotificationResponse> {
  return apiRequest<NotificationResponse>(
    `/organizations/${orgId}/notifications/${notificationId}/read`,
    { method: "POST", token },
  );
}

export async function markAllNotificationsRead(
  orgId: string,
  token: string,
): Promise<number> {
  const data = await apiRequest<{ marked_count: number }>(
    `/organizations/${orgId}/notifications/read-all`,
    { method: "POST", token },
  );
  return data.marked_count;
}

export async function getUserNotificationPreferences(
  orgId: string,
  token: string,
): Promise<UserNotificationPreferencesResponse> {
  return apiRequest<UserNotificationPreferencesResponse>(
    `/organizations/${orgId}/users/me/notification-preferences`,
    { token },
  );
}

export async function patchUserNotificationPreferences(
  orgId: string,
  token: string,
  body: {
    notifications_enabled?: boolean;
    muted_notification_kinds?: string[];
  },
): Promise<UserNotificationPreferencesResponse> {
  return apiRequest<UserNotificationPreferencesResponse>(
    `/organizations/${orgId}/users/me/notification-preferences`,
    { method: "PATCH", token, body: JSON.stringify(body) },
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
