/** UI view models for Risk pages — mapped from API responses only. */

export interface RiskItemView {
  id: string;
  name: string;
  description: string;
  priority: string;
  score: number;
  department: string;
  status: string;
  lifecycleStatus: string;
  owner: string;
  lastUpdated: string;
  category: string;
  sourceType: string;
}

export interface RiskMatrixItemView {
  id: string;
  name: string;
  likelihood: string;
  impact: string;
  priority: string;
}

export interface RiskSeverityChartItem {
  level: string;
  count: number;
}

export interface RiskDepartmentChartItem {
  department: string;
  score: number;
}

export interface RiskCategoryChartItem {
  category: string;
  score: number;
}

export interface RiskMitigationPlanView {
  id: string;
  title: string;
  description: string;
  status: string;
  owner: string;
  targetDate: string;
  relatedRisk: string;
}

export interface RiskRecommendationView {
  id: string;
  title: string;
  description: string;
  priority: string;
  category?: string;
}

export interface RiskFindingView {
  id: string;
  runId: string;
  name: string;
  description: string;
  category: string;
  priority: string;
  score: number;
  likelihood: string;
  impact: string;
  status: string;
  statusCode: string;
  department: string;
  promotedRiskId: string | null;
  detectionRuleId: string;
}

export interface RiskAnalysisHistoryItem {
  id: string;
  title: string;
  date: string;
  status: string;
  findings: number;
  posture: string;
}
