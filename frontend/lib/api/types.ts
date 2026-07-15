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
  department_id: string | null;
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
  department_id: string | null;
  source_file_id: string | null;
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
  organization_id: string;
  recipient_user_id: string;
  platform_event_kind: string;
  title: string;
  body: string;
  source_entity_type: string;
  source_entity_id: string;
  reporting_period_id: string | null;
  materialized_at: string;
  status: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserNotificationPreferencesResponse {
  notifications_enabled: boolean;
  muted_notification_kinds: string[];
  preferences_version: string;
}

export interface UserResponse {
  id: string;
  organization_id: string;
  full_name: string;
  email: string;
  role: "admin" | "executive" | "analyst";
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DepartmentResponse {
  id: string;
  organization_id: string;
  name_ar: string;
  code: string | null;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReportingPeriodResponse {
  id: string;
  organization_id: string;
  label: string;
  start_date: string | null;
  end_date: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ListQueryParams {
  limit?: number;
  offset?: number;
}

export interface TimelineEventResponse {
  id: string;
  title: string;
  event_type: string;
  event_date: string;
}

export interface ImportRecordResponse {
  id: string;
  financial_file_id: string;
  imported_at: string;
  record_count: number | null;
  status: string;
  error_message: string | null;
  created_at: string;
}

export interface DataQualityCheckResponse {
  id: string;
  snapshot_id: string;
  check_name: string;
  result_percent: number;
  details: string | null;
  display_order: number;
}

export interface DataQualitySnapshotResponse {
  id: string;
  organization_id: string;
  reporting_period_id: string | null;
  overall_score: number | null;
  evaluated_at: string;
}

/**
 * Mirrors `ResolvedSettingsResponse` API schema.
 * NOTE: Domain model has pdf_export_* on report_preferences but the API
 * response schema omits them — do not patch or display those fields until
 * backend contract is fixed.
 */
export interface ResolvedSettingsResponse {
  organization_id: string;
  document_version: string;
  organization_identity: {
    name: string;
    platform_name: string;
    executive_title: string | null;
  };
  organization_settings: {
    locale: string;
    date_display_format: string;
    currency_display_code: string;
  };
  localization: {
    prompt_language: string;
    report_language: string;
    prompt_language_source: string;
    report_language_source: string;
  };
  ai_configuration: {
    ai_recommendations_enabled: boolean;
    waste_recommendations_auto_suggest: boolean;
  };
  analysis_configuration: {
    enabled_analysis_types: string[];
    timeline_on_completion_enabled: boolean;
    default_analysis_title_template: string;
    require_ai_insights_before_report: boolean;
  };
  report_preferences: {
    default_report_title_template: string;
    auto_publish_on_generate: boolean;
    include_ai_sections_when_available: boolean;
    include_recommendations_section: boolean;
    include_scenario_provenance_section: boolean;
  };
  platform_default_notification_preferences: {
    notifications_enabled: boolean;
    enabled_notification_kinds: string[];
  };
}

export type SettingsPatchPayload = {
  organization_settings?: Partial<
    ResolvedSettingsResponse["organization_settings"]
  >;
  localization?: Partial<
    Pick<
      ResolvedSettingsResponse["localization"],
      "prompt_language" | "report_language"
    >
  >;
  ai_configuration?: Partial<ResolvedSettingsResponse["ai_configuration"]>;
  analysis_configuration?: Partial<
    ResolvedSettingsResponse["analysis_configuration"]
  >;
  report_preferences?: Partial<ResolvedSettingsResponse["report_preferences"]>;
  platform_default_notification_preferences?: Partial<
    ResolvedSettingsResponse["platform_default_notification_preferences"]
  >;
};
