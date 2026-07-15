export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T | null;
  errors: string[] | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface OrganizationResponse {
  id: string;
  name: string;
  platform_name: string;
  executive_title: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FinancialFileResponse {
  id: string;
  organization_id: string;
  file_name: string;
  size_display: string | null;
  processing_status: string;
  uploaded_at: string;
}

export interface FinancialSnapshotResponse {
  id: string;
  financial_file_id: string;
  snapshot_version: number;
  record_count: number;
}

export interface UploadIngestionResponse {
  financial_file: FinancialFileResponse;
  financial_snapshot: FinancialSnapshotResponse | null;
}

export interface AnalysisRunResponse {
  id: string;
  analysis_type: string;
  title: string;
  status: string;
  source_file_id: string | null;
  source_snapshot_id: string | null;
  completed_at: string | null;
}

export interface WasteDecisionExecuteResponse {
  analysis_run: AnalysisRunResponse;
  snapshot_id: string;
  snapshot_version: number;
}

export interface WasteAnalysisResultResponse {
  total_waste_amount: number;
  waste_percentage: number;
  potential_savings_amount: number | null;
  active_savings_opportunities: number | null;
}

export interface WasteCategoryBreakdownResponse {
  id: string;
  category_name: string;
  amount: number;
  percentage: number;
}

export interface RecommendationResponse {
  id: string;
  title: string;
  description: string;
  priority: string;
  confidence_label: string | null;
  estimated_savings_amount: number | null;
}

export interface WasteAiRecommendationsResponse {
  analysis_run: AnalysisRunResponse;
  recommendation_count: number;
  ai_insights: Record<string, unknown>;
  recommendations: RecommendationResponse[];
}

export interface SimulationScenarioResponse {
  id: string;
  name: string;
  description: string;
  status: string;
}

export interface ScenarioExecuteResponse {
  analysis_run: AnalysisRunResponse;
  simulation_run: { id: string; scenario_id: string };
  archetype: string;
}

export interface SimulationForecastSummaryResponse {
  baseline_label: string;
  baseline_value: string;
  projected_label: string;
  projected_value: string;
  delta_label: string;
  delta_value: string;
  confidence_label: string | null;
}

export interface SimulationChartPointResponse {
  quarter_label: string;
  baseline_amount: number;
  projected_amount: number;
}

export interface SimulationComparisonMetricResponse {
  metric_name: string;
  current_value: string;
  simulated_value: string;
  change_value: string;
}

export interface ReportResponse {
  id: string;
  title: string;
  report_type: string;
  status: string;
  summary: string;
  has_content: boolean;
  created_at: string;
}

export interface ReportContentResponse {
  report_id: string;
  content: {
    sections?: { key: string; payload: Record<string, unknown> }[];
  };
}

export interface ReportGenerateResponse {
  report: ReportResponse;
  profile: string;
}

export interface NotificationResponse {
  id: string;
  title: string;
  body: string;
  platform_event_kind: string;
  is_read: boolean;
  materialized_at: string;
}

export interface TimelineEventResponse {
  id: string;
  title: string;
  event_type: string;
  event_date: string;
}

export interface ImportRecordResponse {
  id: string;
  file_name: string;
  status: string;
  record_count: number | null;
  created_at: string;
}
