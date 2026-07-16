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
  ensureExecutiveArabic,
} from "@/lib/executive-language";
import {
  formatDate,
  mapFindingStatus,
  mapLegacyRiskStatus,
  mapLifecycleStatus,
  mapMitigationPlanStatus,
  mapRecommendationCategory,
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
  RiskExecutiveCardView,
  RiskExposureChartItem,
  RiskFindingView,
  RiskItemView,
  RiskMatrixItemView,
  RiskMitigationPlanView,
  RiskRecommendationView,
  RiskSeverityChartItem,
  RiskTopItemChart,
  RiskTrendChartItem,
} from "@/lib/risk/view-types";

function evidenceStr(evidence: Record<string, unknown>, key: string, fallback = "—"): string {
  const value = evidence[key];
  return typeof value === "string" && value.trim() ? value : fallback;
}

function evidenceFromFinding(finding: RiskFindingResponse): Record<string, unknown> {
  return (finding.evidence ?? {}) as Record<string, unknown>;
}

function execText(value: string, fallback = "—"): string {
  if (!value?.trim() || value === "—") return fallback;
  return ensureExecutiveArabic(value);
}

export function mapFindingToView(
  finding: RiskFindingResponse,
  departmentName: (id: string | null) => string | null,
): RiskFindingView {
  const evidence = evidenceFromFinding(finding);
  const deptFromEvidence = evidenceStr(evidence, "department_ar", "");
  return {
    id: finding.id,
    runId: finding.analysis_run_id,
    name: execText(finding.name),
    description: execText(finding.description),
    category: mapRiskCategoryCode(finding.category_code),
    priority: mapRiskPriority(finding.priority),
    score: finding.score,
    likelihood: mapRiskLevel(finding.likelihood),
    impact: mapRiskLevel(finding.impact),
    status: mapFindingStatus(finding.finding_status),
    statusCode: finding.finding_status,
    department:
      deptFromEvidence !== "—" && deptFromEvidence
        ? execText(deptFromEvidence)
        : finding.department_id
          ? execText(departmentName(finding.department_id) ?? "—")
          : "—",
    supplier: execText(evidenceStr(evidence, "supplier_ar")),
    amountExposed: execText(evidenceStr(evidence, "amount_exposed_label")),
    estimatedSavings: execText(evidenceStr(evidence, "estimated_savings_label")),
    recommendedAction: execText(evidenceStr(evidence, "recommended_action_ar")),
    targetOwner: execText(evidenceStr(evidence, "owner_ar")),
    targetTimeline: execText(evidenceStr(evidence, "target_timeline_ar")),
    confidence:
      typeof evidence.confidence_score === "number"
        ? `${evidence.confidence_score}/100`
        : "—",
    businessImpact: execText(evidenceStr(evidence, "business_impact_ar")),
    ifIgnored: execText(evidenceStr(evidence, "if_ignored_ar")),
    promotedRiskId: finding.promoted_risk_id,
    detectionRuleId: finding.detection_rule_id,
  };
}

export function mapFindingToExecutiveCard(
  finding: RiskFindingView,
  raw?: RiskFindingResponse,
): RiskExecutiveCardView {
  const evidence = raw ? evidenceFromFinding(raw) : {};
  const detectionReason = execText(
    evidenceStr(evidence, "detection_reason_ar", finding.description),
  );
  const executiveSummary = execText(
    evidenceStr(evidence, "executive_summary_ar", finding.description),
  );
  const wasteValue = execText(evidenceStr(evidence, "waste_value_label", finding.amountExposed));
  const financialImpact = execText(
    evidenceStr(evidence, "financial_impact_ar", finding.amountExposed),
  );
  const supplierCountRaw = evidence.supplier_count;
  const supplierCount =
    typeof supplierCountRaw === "string" || typeof supplierCountRaw === "number"
      ? String(supplierCountRaw)
      : "—";
  const evidenceLines = [
    evidenceStr(evidence, "data_source_ar", "") !== "—"
      ? `المصدر: ${evidenceStr(evidence, "data_source_ar")}`
      : null,
    finding.department !== "—" ? `الإدارة: ${finding.department}` : null,
    finding.supplier !== "—" ? `المورد: ${finding.supplier}` : null,
    finding.amountExposed !== "—" ? `التعرّض: ${finding.amountExposed}` : null,
    wasteValue !== "—" ? `الهدر: ${wasteValue}` : null,
  ]
    .filter(Boolean)
    .join(" · ");

  return {
    id: finding.id,
    title: finding.name,
    executiveSummary,
    detectionReason,
    priority: finding.priority,
    department: finding.department,
    supplier: finding.supplier,
    supplierCount,
    affectedCategory: finding.category,
    amountExposed: finding.amountExposed,
    wasteValue,
    probability: finding.likelihood,
    financialImpact,
    businessImpact: finding.businessImpact,
    executiveExplanation: finding.description,
    recommendedAction: finding.recommendedAction,
    estimatedSavings: finding.estimatedSavings,
    targetOwner: finding.targetOwner,
    targetTimeline: finding.targetTimeline,
    confidence: finding.confidence,
    evidenceSummary: evidenceLines || finding.description,
    ifIgnored: finding.ifIgnored,
    score: finding.score,
    likelihood: finding.likelihood,
    impact: finding.impact,
  };
}

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

export function buildDepartmentChartFromFindings(
  findings: RiskFindingResponse[],
): RiskDepartmentChartItem[] {
  const buckets = new Map<string, { total: number; count: number }>();
  for (const item of findings) {
    const evidence = evidenceFromFinding(item);
    const label = evidenceStr(evidence, "department_ar", "غير محدد");
    const prev = buckets.get(label) ?? { total: 0, count: 0 };
    buckets.set(label, { total: prev.total + item.score, count: prev.count + 1 });
  }
  return Array.from(buckets.entries())
    .map(([department, stats]) => ({
      department,
      score: Math.round(stats.total / stats.count),
    }))
    .sort((a, b) => b.score - a.score);
}

export function buildExposureByDepartment(
  findings: RiskFindingResponse[],
): RiskExposureChartItem[] {
  const buckets = new Map<string, number>();
  for (const item of findings) {
    const evidence = evidenceFromFinding(item);
    const dept = evidenceStr(evidence, "department_ar", "غير محدد");
    const raw = evidence.amount_exposed_sar;
    const amount =
      typeof raw === "string" || typeof raw === "number" ? Number(raw) || 0 : 0;
    buckets.set(dept, (buckets.get(dept) ?? 0) + amount);
  }
  return Array.from(buckets.entries())
    .map(([label, amount]) => ({
      label,
      amount,
      formatted: amount.toLocaleString("ar-SA"),
    }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 10);
}

export function buildSupplierExposureChart(
  findings: RiskFindingResponse[],
): RiskExposureChartItem[] {
  const buckets = new Map<string, number>();
  for (const item of findings) {
    const evidence = evidenceFromFinding(item);
    const supplier = evidenceStr(evidence, "supplier_ar", "");
    if (!supplier || supplier === "—") continue;
    const raw = evidence.amount_exposed_sar;
    const amount =
      typeof raw === "string" || typeof raw === "number" ? Number(raw) || 0 : 0;
    buckets.set(supplier, (buckets.get(supplier) ?? 0) + amount);
  }
  return Array.from(buckets.entries())
    .map(([label, amount]) => ({
      label,
      amount,
      formatted: amount.toLocaleString("ar-SA"),
    }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 10);
}

export function buildSavingsChart(
  findings: RiskFindingResponse[],
): RiskExposureChartItem[] {
  return findings
    .map((item) => {
      const evidence = evidenceFromFinding(item);
      const raw = evidence.estimated_savings_sar;
      const amount =
        typeof raw === "string" || typeof raw === "number" ? Number(raw) || 0 : 0;
      return {
        label: item.name.slice(0, 40),
        amount,
        formatted: amount.toLocaleString("ar-SA"),
      };
    })
    .filter((x) => x.amount > 0)
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 10);
}

export function buildTopRisksChart(findings: RiskFindingResponse[]): RiskTopItemChart[] {
  return [...findings]
    .sort((a, b) => b.score - a.score)
    .slice(0, 10)
    .map((item) => {
      const evidence = evidenceFromFinding(item);
      return {
        name: item.name.slice(0, 36),
        score: item.score,
        priority: mapRiskPriority(item.priority),
        department: evidenceStr(evidence, "department_ar", "—"),
      };
    });
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

export function buildWasteByDepartment(
  findings: RiskFindingResponse[],
): RiskExposureChartItem[] {
  const buckets = new Map<string, number>();
  for (const item of findings) {
    const evidence = evidenceFromFinding(item);
    const share = evidence.share_of_waste;
    if (share === undefined && !evidence.waste_value_sar) continue;
    const dept = evidenceStr(evidence, "department_ar", "غير محدد");
    const raw = evidence.waste_value_sar ?? evidence.amount_exposed_sar;
    const amount =
      typeof raw === "string" || typeof raw === "number" ? Number(raw) || 0 : 0;
    if (amount <= 0) continue;
    buckets.set(dept, (buckets.get(dept) ?? 0) + amount);
  }
  if (buckets.size === 0) {
    for (const item of findings) {
      const evidence = evidenceFromFinding(item);
      const dept = evidenceStr(evidence, "department_ar", "غير محدد");
      const raw = evidence.amount_exposed_sar;
      const amount =
        typeof raw === "string" || typeof raw === "number" ? Number(raw) || 0 : 0;
      buckets.set(dept, (buckets.get(dept) ?? 0) + amount);
    }
  }
  return Array.from(buckets.entries())
    .map(([label, amount]) => ({
      label,
      amount,
      formatted: amount.toLocaleString("ar-SA"),
    }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 10);
}

export function buildRiskTrendFromHistory(
  history: RiskAnalysisHistoryItem[],
): RiskTrendChartItem[] {
  return [...history]
    .reverse()
    .slice(-8)
    .map((item) => ({
      label: item.date,
      findings: item.findings,
      posture: item.posture,
    }));
}

export function buildMatrixItems(findings: RiskFindingResponse[]): RiskMatrixItemView[] {
  return findings.map((item) => {
    const view = mapFindingToView(item, () => null);
    const evidence = evidenceFromFinding(item);
    const why = execText(
      evidenceStr(evidence, "detection_reason_ar", item.description),
    );
    const tooltip = [
      why,
      view.department !== "—" ? `الإدارة: ${view.department}` : null,
      view.amountExposed !== "—" ? `التعرّض: ${view.amountExposed}` : null,
      view.supplier !== "—" ? `المورد: ${view.supplier}` : null,
    ]
      .filter(Boolean)
      .join("\n");
    return {
      id: item.id,
      name: view.name,
      likelihood: mapRiskLevel(item.likelihood),
      impact: mapRiskLevel(item.impact),
      priority: mapRiskPriority(item.priority),
      department: view.department,
      supplier: view.supplier,
      amountExposed: view.amountExposed,
      score: item.score,
      tooltip,
      whyTooltip: why,
    };
  });
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
    title: ensureExecutiveArabic(rec.title),
    description: ensureExecutiveArabic(rec.description),
    priority: mapRiskPriority(rec.priority),
    category:
      typeof rec.source_context?.recommendation_category === "string"
        ? mapRecommendationCategory(String(rec.source_context.recommendation_category))
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
