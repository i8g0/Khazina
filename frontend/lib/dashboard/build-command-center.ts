import type {
  AnalysisRunResponse,
  RecommendationResponse,
  ReportResponse,
  RiskAnalysisResultResponse,
  RiskResponse,
  WasteAnalysisResultResponse,
  WasteCategoryBreakdownResponse,
  WasteVendorFindingResponse,
} from "@/lib/api/types";
import { formatCurrency, formatPercent, sanitizeExecutiveText } from "@/lib/format";
import { navRouteMap } from "@/lib/app-nav";
import type {
  DecisionPipelineStep,
  ExecutiveAlert,
  ExecutiveCommandCenterModel,
  ExecutiveHealthLevel,
  ExecutiveIndicator,
  StoryTimelineStep,
} from "@/lib/dashboard/command-center-types";

const HEALTH_LABELS: Record<ExecutiveHealthLevel, string> = {
  excellent: "ممتاز",
  good: "جيد",
  needs_attention: "يحتاج انتباهاً",
  critical: "حرج",
};

function healthFromScore(score: number): ExecutiveHealthLevel {
  if (score >= 85) return "excellent";
  if (score >= 70) return "good";
  if (score >= 50) return "needs_attention";
  return "critical";
}

function latestRun(
  runs: AnalysisRunResponse[],
  types: string[],
): AnalysisRunResponse | undefined {
  return runs.find(
    (run) =>
      types.includes(run.analysis_type) &&
      run.status === "completed",
  );
}

function insights(run?: AnalysisRunResponse): Record<string, unknown> | undefined {
  return run?.runtime_metadata?.ai_insights as Record<string, unknown> | undefined;
}

function simulationMeta(run?: AnalysisRunResponse): Record<string, unknown> | undefined {
  if (!run?.runtime_metadata) return undefined;
  return run.runtime_metadata as Record<string, unknown>;
}

function topDepartmentByRisk(
  risks: RiskResponse[],
  departmentName: (id: string | null) => string | null,
): string | null {
  const open = risks.filter((r) => r.status !== "closed");
  const counts = new Map<string, number>();
  for (const risk of open) {
    const key = departmentName(risk.department_id) ?? "غير محددة";
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  let best: string | null = null;
  let max = 0;
  for (const [name, count] of counts) {
    if (count > max) {
      max = count;
      best = name;
    }
  }
  return best;
}

function topVendor(
  vendors: WasteVendorFindingResponse[],
): { name: string; amount: number } | null {
  if (vendors.length === 0) return null;
  const sorted = [...vendors].sort((a, b) => b.amount - a.amount);
  return { name: sorted[0].vendor_name, amount: sorted[0].amount };
}

function aggregateDepartmentWaste(
  rows: WasteCategoryBreakdownResponse[],
  departmentName: (id: string | null) => string | null,
): { label: string; amount: number }[] {
  const totals = new Map<string, number>();
  for (const row of rows) {
    const label =
      (row.department_id ? departmentName(row.department_id) : null) ??
      row.category_name;
    totals.set(label, (totals.get(label) ?? 0) + row.amount);
  }
  return [...totals.entries()]
    .map(([label, amount]) => ({ label, amount }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 6);
}

function buildBriefParts(
  wasteRun?: AnalysisRunResponse,
  riskRun?: AnalysisRunResponse,
  simRun?: AnalysisRunResponse,
): { domain: string; text: string }[] {
  const parts: { domain: string; text: string }[] = [];
  const wasteInsights = insights(wasteRun);
  const riskInsights = insights(riskRun);
  const simJudgment = simulationMeta(simRun)?.executive_judgment as
    | Record<string, unknown>
    | undefined;

  const wasteSummary = wasteInsights?.executive_summary;
  if (typeof wasteSummary === "string" && wasteSummary.trim()) {
    parts.push({
      domain: "الهدر",
      text: sanitizeExecutiveText(wasteSummary),
    });
  }

  const riskSummary = riskInsights?.risk_executive_summary;
  if (typeof riskSummary === "string" && riskSummary.trim()) {
    parts.push({
      domain: "المخاطر",
      text: sanitizeExecutiveText(riskSummary),
    });
  }

  const simVerdict =
    (typeof simJudgment?.executive_verdict === "string" &&
      simJudgment.executive_verdict) ||
    (typeof simJudgment?.strategic_recommendation === "string" &&
      simJudgment.strategic_recommendation);
  if (typeof simVerdict === "string" && simVerdict.trim()) {
    parts.push({
      domain: "المحاكاة",
      text: sanitizeExecutiveText(simVerdict),
    });
  }

  return parts;
}

function buildStorySteps(
  runs: AnalysisRunResponse[],
  wasteResult: WasteAnalysisResultResponse | null,
  riskResult: RiskAnalysisResultResponse | null,
  simRun: AnalysisRunResponse | undefined,
  reports: ReportResponse[],
  departmentName: (id: string | null) => string | null,
  fileName: (id: string | null) => string | null,
): StoryTimelineStep[] {
  const steps: StoryTimelineStep[] = [];
  const uploadRun = runs.find((r) => r.source_file_id);
  if (uploadRun?.source_file_id) {
    steps.push({
      id: "upload",
      title: "تم رفع البيانات المالية",
      detail: fileName(uploadRun.source_file_id) ?? "ملف مالي",
      href: navRouteMap.data,
    });
  }

  if (wasteResult) {
    const opportunities = wasteResult.active_savings_opportunities ?? 0;
    steps.push({
      id: "waste",
      title:
        opportunities > 0
          ? `اكتشف التحليل ${opportunities} فرصة هدر`
          : "اكتمل تحليل الهدر المالي",
      detail: `إجمالي الهدر: ${formatCurrency(wasteResult.total_waste_amount)} (${formatPercent(wasteResult.waste_percentage)})`,
      href: navRouteMap.waste,
    });
  }

  if (riskResult) {
    steps.push({
      id: "risk",
      title: `حدّد محرك المخاطر ${riskResult.high_priority_count} مخاطر حرجة`,
      detail: `الوضع العام: ${riskResult.overall_posture_level}`,
      href: navRouteMap.risk,
    });
  }

  if (simRun) {
    const judgment = simulationMeta(simRun)?.executive_judgment as
      | Record<string, unknown>
      | undefined;
    const recommendation =
      typeof judgment?.recommendation === "string"
        ? judgment.recommendation
        : null;
    steps.push({
      id: "simulation",
      title: recommendation
        ? `توصية المحاكاة: ${recommendation}`
        : "اكتملت محاكاة الأعمال",
      detail:
        typeof judgment?.executive_verdict === "string"
          ? sanitizeExecutiveText(judgment.executive_verdict).slice(0, 160)
          : undefined,
      href: navRouteMap.simulation,
    });
  }

  if (wasteResult?.potential_savings_amount) {
    steps.push({
      id: "savings",
      title: `الوفورات السنوية المقدرة: ${formatCurrency(wasteResult.potential_savings_amount)}`,
      href: navRouteMap.waste,
    });
  }

  const riskInsights = insights(
    runs.find((r) => r.analysis_type === "risk"),
  );
  const boardReport = riskInsights?.risk_board_report;
  if (typeof boardReport === "string" && boardReport.trim()) {
    steps.push({
      id: "board",
      title: "توصية مجلس الإدارة متاحة",
      detail: sanitizeExecutiveText(boardReport).slice(0, 160),
      href: navRouteMap.reports,
    });
  } else if (reports.length > 0) {
    steps.push({
      id: "reports",
      title: "تقرير تنفيذي جاهز للمراجعة",
      detail: reports[0]?.title,
      href: navRouteMap.reports,
    });
  }

  return steps;
}

export interface BuildCommandCenterInput {
  runs: AnalysisRunResponse[];
  recommendations: RecommendationResponse[];
  risks: RiskResponse[];
  wasteResult: WasteAnalysisResultResponse | null;
  wasteBreakdowns: WasteCategoryBreakdownResponse[];
  vendors: WasteVendorFindingResponse[];
  riskResult: RiskAnalysisResultResponse | null;
  reports: ReportResponse[];
  departmentName: (id: string | null) => string | null;
  fileName: (id: string | null) => string | null;
}

export function buildExecutiveCommandCenter(
  input: BuildCommandCenterInput,
): ExecutiveCommandCenterModel {
  const {
    runs,
    recommendations,
    risks,
    wasteResult,
    wasteBreakdowns,
    vendors,
    riskResult,
    reports,
    departmentName,
    fileName,
  } = input;

  const wasteRun = latestRun(runs, ["financial_waste", "waste"]);
  const riskRun = latestRun(runs, ["risk"]);
  const simRun = latestRun(runs, ["simulation"]);

  const briefParts = buildBriefParts(wasteRun, riskRun, simRun);
  const brief =
    briefParts.length > 0
      ? briefParts.map((p) => p.text).join(" ")
      : null;

  const urgentRecs = recommendations.filter((r) => r.priority === "high");
  const leadingVendor = topVendor(vendors);
  const topRiskDept = topDepartmentByRisk(risks, departmentName);
  const moneyAtRisk =
    (wasteResult?.total_waste_amount ?? 0) +
    (riskResult?.high_priority_count ?? 0) * 250_000;

  let healthScore = 55;
  if (wasteResult) {
    if (wasteResult.waste_percentage <= 10) healthScore += 12;
    else if (wasteResult.waste_percentage <= 20) healthScore += 4;
    else healthScore -= 18;
  }
  if (riskResult) {
    const posture = riskResult.overall_posture_level.toLowerCase();
    if (posture.includes("low")) healthScore += 14;
    else if (posture.includes("medium")) healthScore += 2;
    else healthScore -= 16;
    healthScore -= Math.min(riskResult.high_priority_count * 4, 20);
  }
  if (wasteRun && insights(wasteRun)) healthScore += 6;
  if (riskRun && insights(riskRun)) healthScore += 6;
  if (simRun) healthScore += 8;
  if (reports.length > 0) healthScore += 5;
  if (urgentRecs.length === 0 && wasteResult) healthScore += 4;
  healthScore = Math.max(0, Math.min(100, healthScore));

  const healthLevel = healthFromScore(healthScore);
  const hasAi =
    Boolean(insights(wasteRun)) ||
    Boolean(insights(riskRun)) ||
    Boolean(simulationMeta(simRun)?.executive_judgment);

  const indicators: ExecutiveIndicator[] = [
    {
      id: "money-at-risk",
      label: "أموال معرضة للخطر",
      value: moneyAtRisk > 0 ? formatCurrency(moneyAtRisk) : null,
      href: navRouteMap.risk,
      emptyMessage: "نفّذ تحليل الهدر والمخاطر",
    },
    {
      id: "recoverable-savings",
      label: "وفورات قابلة للاسترداد",
      value:
        wasteResult?.potential_savings_amount != null
          ? formatCurrency(wasteResult.potential_savings_amount)
          : null,
      href: navRouteMap.waste,
      emptyMessage: "ستظهر بعد كشف الهدر",
    },
    {
      id: "top-risk-dept",
      label: "أعلى إدارة مخاطر",
      value: topRiskDept,
      href: navRouteMap.risk,
      emptyMessage: "لا مخاطر مسجّلة بعد",
    },
    {
      id: "top-waste-vendor",
      label: "أعلى مورد هدر",
      value: leadingVendor
        ? `${leadingVendor.name} (${formatCurrency(leadingVendor.amount)})`
        : null,
      href: navRouteMap.waste,
      emptyMessage: "ستظهر بعد تحليل الموردين",
    },
    {
      id: "urgent-decisions",
      label: "قرارات عاجلة",
      value:
        urgentRecs.length > 0 ? String(urgentRecs.length) : null,
      hint: urgentRecs.length > 0 ? "توصية عالية الأولوية" : undefined,
      href: navRouteMap.waste,
      emptyMessage: "لا قرارات عاجلة",
    },
    {
      id: "simulation-readiness",
      label: "جاهزية المحاكاة",
      value: simRun
        ? "جاهز"
        : wasteRun && riskRun
          ? "يمكن التشغيل"
          : null,
      href: navRouteMap.simulation,
      emptyMessage: "أكمل الهدر والمخاطر أولاً",
    },
    {
      id: "ai-confidence",
      label: "ثقة التحليل",
      value: hasAi ? "عالية" : wasteRun || riskRun ? "متوسطة" : null,
      href: navRouteMap.waste,
      emptyMessage: "بانتظار رؤى الذكاء الاصطناعي",
    },
    {
      id: "board-attention",
      label: "انتباه مجلس الإدارة",
      value:
        (riskResult?.high_priority_count ?? 0) >= 3
          ? "مرتفع"
          : (riskResult?.high_priority_count ?? 0) >= 1
            ? "متوسط"
            : reports.length > 0
              ? "منخفض"
              : null,
      href: navRouteMap.reports,
      emptyMessage: "لا يتطلب تدخلاً فورياً",
    },
  ];

  const alerts: ExecutiveAlert[] = [];
  if (wasteResult && wasteResult.waste_percentage >= 20) {
    alerts.push({
      id: "high-waste",
      title: "هدر مالي مرتفع",
      description: `نسبة الهدر ${formatPercent(wasteResult.waste_percentage)} — يتطلب تدخلاً تنفيذياً`,
      href: navRouteMap.waste,
      severity: "critical",
    });
  }
  if ((riskResult?.high_priority_count ?? 0) > 0) {
    alerts.push({
      id: "critical-risks",
      title: "مخاطر حرجة مفتوحة",
      description: `${riskResult?.high_priority_count} مخاطر ذات أولوية عالية`,
      href: navRouteMap.risk,
      severity: "critical",
    });
  }
  if (leadingVendor && wasteResult && leadingVendor.amount > wasteResult.total_waste_amount * 0.3) {
    alerts.push({
      id: "vendor-concentration",
      title: "تركّز مورد حرج",
      description: `${leadingVendor.name} يساهم بشكل غير متناسب في الهدر`,
      href: navRouteMap.waste,
      severity: "warning",
    });
  }
  if (wasteRun && riskRun && !simRun) {
    alerts.push({
      id: "sim-ready",
      title: "المحاكاة متاحة",
      description: "البيانات جاهزة لاختبار سيناريو قرار تنفيذي",
      href: navRouteMap.simulation,
      severity: "info",
    });
  }
  if (reports.length === 0 && wasteRun && riskRun) {
    alerts.push({
      id: "report-pending",
      title: "تقرير مجلس معلّق",
      description: "أنشئ تقريراً تنفيذياً لإكمال دورة القرار",
      href: navRouteMap.reports,
      severity: "info",
    });
  }

  const pipeline: DecisionPipelineStep[] = [
    {
      id: "upload",
      label: "رفع البيانات",
      completed: runs.some((r) => Boolean(r.source_file_id)),
      href: navRouteMap.data,
    },
    {
      id: "waste",
      label: "كشف الهدر",
      completed: Boolean(wasteRun),
      href: navRouteMap.waste,
      detail: wasteResult
        ? formatCurrency(wasteResult.total_waste_amount)
        : undefined,
    },
    {
      id: "risk",
      label: "تقييم المخاطر",
      completed: Boolean(riskRun),
      href: navRouteMap.risk,
      detail: riskResult
        ? `${riskResult.total_findings} نتيجة`
        : undefined,
    },
    {
      id: "simulation",
      label: "محاكاة الأعمال",
      completed: Boolean(simRun),
      href: navRouteMap.simulation,
    },
    {
      id: "reports",
      label: "التقارير",
      completed: reports.length > 0,
      href: navRouteMap.reports,
      detail: reports.length > 0 ? `${reports.length} تقرير` : undefined,
    },
    {
      id: "recommendation",
      label: "التوصية التنفيذية",
      completed:
        recommendations.length > 0 ||
        Boolean(insights(wasteRun)) ||
        Boolean(insights(riskRun)),
      href: navRouteMap.waste,
    },
  ];

  const storySteps = buildStorySteps(
    runs,
    wasteResult,
    riskResult,
    simRun,
    reports,
    departmentName,
    fileName,
  );

  const riskInsights = insights(riskRun);
  const boardRecommendation =
    typeof riskInsights?.risk_board_report === "string"
      ? sanitizeExecutiveText(riskInsights.risk_board_report).slice(0, 200)
      : null;

  const narrativeStatus =
    (typeof insights(wasteRun)?.narrative_status === "string" &&
      insights(wasteRun)?.narrative_status) ||
    (typeof insights(riskRun)?.narrative_status === "string" &&
      insights(riskRun)?.narrative_status) ||
    null;

  return {
    brief,
    briefParts,
    healthScore,
    healthLevel,
    healthLabelAr: HEALTH_LABELS[healthLevel],
    indicators,
    alerts,
    pipeline,
    storySteps,
    departmentChart: aggregateDepartmentWaste(wasteBreakdowns, departmentName),
    boardRecommendation,
    narrativeStatus:
      typeof narrativeStatus === "string" ? narrativeStatus : null,
  };
}
