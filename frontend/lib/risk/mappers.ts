import type {
  AnalysisRunResponse,
  MitigationPlanResponse,
  RecommendationResponse,
  RiskAnalysisResultResponse,
  RiskAnalysisResultSummary,
  RiskFindingResponse,
  RiskResponse,
} from "@/lib/api/types";
import {
  formatDate,
  mapFindingStatus,
  mapLegacyRiskStatus,
  mapLifecycleStatus,
  mapMitigationPlanStatus,
  mapRiskCategoryCode,
  mapRiskLevel,
  mapRiskPosture,
  mapRiskPriority,
  mapRiskSourceType,
  mapRunStatus,
} from "@/lib/format";
import type {
  RiskAnalysisHistoryItem,
  RiskCategoryChartItem,
  RiskDepartmentChartItem,
  RiskFindingView,
  RiskItemView,
  RiskMatrixItemView,
  RiskMitigationPlanView,
  RiskRecommendationView,
  RiskSeverityChartItem,
} from "@/lib/risk/view-types";

export function mapRiskToItemView(
  risk: RiskResponse,
  departmentName: (id: string | null) => string | null,
): RiskItemView {
  return {
    id: risk.id,
    name: risk.name,
    description: risk.description,
    priority: mapRiskPriority(risk.priority),
    score: risk.score,
    department: risk.department_id
      ? departmentName(risk.department_id) ?? "—"
      : "—",
    status: mapLegacyRiskStatus(risk.status),
    lifecycleStatus: mapLifecycleStatus(risk.lifecycle_status),
    owner: risk.owner_label ?? "—",
    lastUpdated: risk.last_updated_at,
    category: risk.category_label ?? mapRiskCategoryCode(risk.category_code),
    sourceType: mapRiskSourceType(risk.source_type),
  };
}

export function mapFindingToView(
  finding: RiskFindingResponse,
  departmentName: (id: string | null) => string | null,
): RiskFindingView {
  return {
    id: finding.id,
    runId: finding.analysis_run_id,
    name: finding.name,
    description: finding.description,
    category: mapRiskCategoryCode(finding.category_code),
    priority: mapRiskPriority(finding.priority),
    score: finding.score,
    likelihood: mapRiskLevel(finding.likelihood),
    impact: mapRiskLevel(finding.impact),
    status: mapFindingStatus(finding.finding_status),
    statusCode: finding.finding_status,
    department: finding.department_id
      ? departmentName(finding.department_id) ?? "—"
      : "—",
    promotedRiskId: finding.promoted_risk_id,
    detectionRuleId: finding.detection_rule_id,
  };
}

export function buildSeverityChart(
  summary: RiskAnalysisResultSummary | RiskAnalysisResultResponse,
): RiskSeverityChartItem[] {
  return [
    { level: "عالية", count: summary.high_priority_count },
    { level: "متوسطة", count: summary.medium_priority_count },
    { level: "منخفضة", count: summary.low_priority_count },
  ];
}

export function buildCategoryChart(
  findings: RiskFindingResponse[],
): RiskCategoryChartItem[] {
  const buckets = new Map<string, { total: number; count: number }>();
  for (const item of findings) {
    const label = mapRiskCategoryCode(item.category_code);
    const prev = buckets.get(label) ?? { total: 0, count: 0 };
    buckets.set(label, {
      total: prev.total + item.score,
      count: prev.count + 1,
    });
  }
  return Array.from(buckets.entries())
    .map(([category, stats]) => ({
      category,
      score: Math.round(stats.total / stats.count),
    }))
    .sort((a, b) => b.score - a.score);
}

export function buildDepartmentChart(
  risks: RiskResponse[],
  departmentName: (id: string | null) => string | null,
): RiskDepartmentChartItem[] {
  const buckets = new Map<string, { total: number; count: number }>();
  for (const risk of risks) {
    const label = risk.department_id
      ? departmentName(risk.department_id) ?? "غير محدد"
      : "غير محدد";
    const prev = buckets.get(label) ?? { total: 0, count: 0 };
    buckets.set(label, { total: prev.total + risk.score, count: prev.count + 1 });
  }
  return Array.from(buckets.entries())
    .map(([department, stats]) => ({
      department,
      score: Math.round(stats.total / stats.count),
    }))
    .sort((a, b) => b.score - a.score);
}

export function buildMatrixItems(findings: RiskFindingResponse[]): RiskMatrixItemView[] {
  return findings.map((item) => ({
    id: item.id,
    name: item.name,
    likelihood: mapRiskLevel(item.likelihood),
    impact: mapRiskLevel(item.impact),
    priority: mapRiskPriority(item.priority),
  }));
}

export function mapMitigationPlan(
  plan: MitigationPlanResponse,
  riskNameById: Map<string, string>,
): RiskMitigationPlanView {
  return {
    id: plan.id,
    title: plan.title,
    description: plan.description,
    status: mapMitigationPlanStatus(plan.status),
    owner: plan.owner_label ?? "—",
    targetDate: plan.target_date,
    relatedRisk: riskNameById.get(plan.risk_id) ?? plan.risk_id,
  };
}

export function mapRecommendation(rec: RecommendationResponse): RiskRecommendationView {
  return {
    id: rec.id,
    title: rec.title,
    description: rec.description,
    priority: mapRiskPriority(rec.priority),
    category:
      typeof rec.source_context?.recommendation_category === "string"
        ? rec.source_context.recommendation_category
        : undefined,
    source_context: rec.source_context ?? null,
  };
}

export function mapAnalysisRunToHistory(
  run: AnalysisRunResponse,
  summary?: RiskAnalysisResultSummary | null,
): RiskAnalysisHistoryItem {
  const meta = run.runtime_metadata as
    | { risk_analysis?: { overall_posture_level?: string; total_findings?: number } }
    | null
    | undefined;
  const posture =
    summary?.overall_posture_level ??
    meta?.risk_analysis?.overall_posture_level ??
    "—";
  const findings =
    summary?.total_findings ?? meta?.risk_analysis?.total_findings ?? 0;
  return {
    id: run.id,
    title: run.title,
    date: run.completed_at ? formatDate(run.completed_at) : "—",
    status: mapRunStatus(run.status),
    findings,
    posture: mapRiskPosture(String(posture)),
  };
}

export function countActiveRisks(risks: RiskResponse[]): number {
  return risks.filter((r) => r.status !== "closed").length;
}

export function countCriticalRisks(
  risks: RiskResponse[],
  summary?: RiskAnalysisResultSummary | RiskAnalysisResultResponse | null,
): number {
  const registerHigh = risks.filter(
    (r) => r.priority === "high" && r.status !== "closed",
  ).length;
  if (registerHigh > 0) return registerHigh;
  return summary?.high_priority_count ?? 0;
}
