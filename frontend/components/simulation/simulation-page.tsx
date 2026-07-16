"use client";

import * as React from "react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { SimulationExecutiveJudgment } from "@/components/simulation/simulation-executive-judgment";
import { SimulationActionPanel } from "@/components/simulation/simulation-action-panel";
import { SimulationAssumptions } from "@/components/simulation/simulation-assumptions";
import { SimulationComparisonChart } from "@/components/simulation/simulation-comparison-chart";
import { SimulationImpactBreakdown } from "@/components/simulation/simulation-impact-breakdown";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PageHero } from "@/components/ui/page-hero";
import { Textarea } from "@/components/ui/textarea";
import Link from "next/link";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavGroups,
  navRouteMap,
} from "@/lib/app-nav";
import { WorkflowIndicator } from "@/components/workflow/workflow-indicator";
import { OperationLoadingPanel } from "@/components/workflow/operation-loading-panel";
import { AuthLoadingShell } from "@/components/workflow/auth-loading-shell";
import { EXECUTIVE_MESSAGES } from "@/lib/workflow/messages";
import {
  useRequireAuth,
  formatApiError,
} from "@/lib/auth/auth-context";
import { useOrganizationDisplay } from "@/lib/org-lookups";
import {
  executeAISimulation,
  getAnalysisRun,
  getForecastSummary,
  listActionItems,
  listChartPoints,
  listComparisonMetrics,
  listImpactItems,
} from "@/lib/api/khazina-api";
import type {
  FinancialRealityPayload,
  InterpretedScenarioPayload,
  SimulationExplanationPayload,
} from "@/lib/api/types";
import { ensureExecutiveArabic, mapScenarioType } from "@/lib/executive-language";
import { writeDemoArtifacts } from "@/lib/demo/state";
import { useDemoArtifacts } from "@/lib/demo/hooks";

const SCENARIO_PLACEHOLDER =
  "اكتب سيناريوك باللغة الطبيعية، مثل:\n" +
  "• أريد زيادة الأرباح 200 ألف ريال\n" +
  "• خفض ميزانية التسويق 15%\n" +
  "• إغلاق فرعين\n" +
  "• رفع الرواتب 8%\n" +
  "• تقليل تكلفة الموردين الرئيسيين";

function mapImpactDirection(
  direction: string,
): "up" | "down" | "neutral" {
  if (direction === "up" || direction === "down") {
    return direction;
  }
  return "neutral";
}

function parseInterpretedScenario(
  value: unknown,
): InterpretedScenarioPayload | null {
  if (!value || typeof value !== "object") return null;
  const record = value as Record<string, unknown>;
  if (typeof record.title_ar !== "string" || !Array.isArray(record.actions)) {
    return null;
  }
  return value as InterpretedScenarioPayload;
}

function parseExplanation(value: unknown): SimulationExplanationPayload | null {
  if (!value || typeof value !== "object") return null;
  const record = value as Record<string, unknown>;
  if (typeof record.executive_summary !== "string") return null;
  return value as SimulationExplanationPayload;
}

function parseFinancialReality(value: unknown): FinancialRealityPayload | null {
  if (!value || typeof value !== "object") return null;
  const record = value as Record<string, unknown>;
  if (
    typeof record.confidence_level !== "string" ||
    typeof record.confidence_score !== "number"
  ) {
    return null;
  }
  return value as FinancialRealityPayload;
}

function formatSar(value: number): string {
  return `${value.toLocaleString("ar-SA", { maximumFractionDigits: 0 })} ر.س`;
}

function confidenceLabel(level: string): string {
  if (level === "high") return "عالية";
  if (level === "medium") return "متوسطة";
  if (level === "low") return "منخفضة";
  return level;
}

export function SimulationPage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const artifacts = useDemoArtifacts();
  const [executing, setExecuting] = React.useState(false);
  const [hydrating, setHydrating] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [userRequest, setUserRequest] = React.useState("");
  const [lastRequest, setLastRequest] = React.useState<string | null>(null);
  const [interpreted, setInterpreted] =
    React.useState<InterpretedScenarioPayload | null>(null);
  const [explanation, setExplanation] =
    React.useState<SimulationExplanationPayload | null>(null);
  const [financialReality, setFinancialReality] =
    React.useState<FinancialRealityPayload | null>(null);
  const [hasRunResults, setHasRunResults] = React.useState(false);
  const [forecast, setForecast] = React.useState<{
    baseline: string;
    projected: string;
    delta: string;
    confidence: string | null;
  } | null>(null);
  const [chartPoints, setChartPoints] = React.useState<
    { quarter: string; baseline: number; projected: number }[]
  >([]);
  const [comparisons, setComparisons] = React.useState<
    { name: string; current: string; simulated: string; change: string }[]
  >([]);
  const [impactItems, setImpactItems] = React.useState<
    {
      id: string;
      category: string;
      baseline: string;
      projected: string;
      change: string;
      direction: "up" | "down" | "neutral";
    }[]
  >([]);
  const [actionItems, setActionItems] = React.useState<
    { id: string; title: string; description: string; status: string }[]
  >([]);

  const loadRunResults = React.useCallback(
    async (runId: string) => {
      if (!auth.session) return;
      const [summary, points, metrics, impacts, actions] = await Promise.all([
        getForecastSummary(auth.session.organizationId, auth.session.token, runId),
        listChartPoints(auth.session.organizationId, auth.session.token, runId),
        listComparisonMetrics(
          auth.session.organizationId,
          auth.session.token,
          runId,
        ),
        listImpactItems(auth.session.organizationId, auth.session.token, runId),
        listActionItems(auth.session.organizationId, auth.session.token, runId),
      ]);
      if (summary) {
        setForecast({
          baseline: summary.baseline_value,
          projected: summary.projected_value,
          delta: summary.delta_value,
          confidence: summary.confidence_label,
        });
        setHasRunResults(true);
      } else {
        setForecast(null);
        setHasRunResults(false);
      }
      setChartPoints(
        points.map((p) => ({
          quarter: p.quarter_label,
          baseline: p.baseline_amount,
          projected: p.projected_amount,
        })),
      );
      setComparisons(
        metrics.map((m) => ({
          name: m.metric_name,
          current: m.current_value,
          simulated: m.simulated_value,
          change: m.change_value,
        })),
      );
      setImpactItems(
        impacts.map((item) => ({
          id: item.id,
          category: item.category_label,
          baseline: item.baseline_value,
          projected: item.projected_value,
          change: item.change_value,
          direction: mapImpactDirection(item.direction),
        })),
      );
      setActionItems(
        actions.map((item) => ({
          id: item.id,
          title: item.title,
          description: item.description,
          status: item.status,
        })),
      );
    },
    [auth.session],
  );

  const hydrateFromAnalysisRun = React.useCallback(
    async (analysisRunId: string) => {
      if (!auth.session) return;
      setHydrating(true);
      try {
        const run = await getAnalysisRun(
          auth.session.organizationId,
          auth.session.token,
          analysisRunId,
        );
        const metadata = run.runtime_metadata ?? {};
        setLastRequest(
          typeof metadata.user_request === "string" ? metadata.user_request : null,
        );
        setInterpreted(parseInterpretedScenario(metadata.interpreted_scenario));
        setExplanation(parseExplanation(metadata.ai_explanation));
        setFinancialReality(parseFinancialReality(metadata.financial_reality));
      } catch {
        /* keep partial UI */
      } finally {
        setHydrating(false);
      }
    },
    [auth.session],
  );

  const resetRunResults = React.useCallback(() => {
    setHasRunResults(false);
    setForecast(null);
    setChartPoints([]);
    setComparisons([]);
    setImpactItems([]);
    setActionItems([]);
    setInterpreted(null);
    setExplanation(null);
    setFinancialReality(null);
    setLastRequest(null);
  }, []);

  const runScenario = async () => {
    if (!auth.session) return;
    const request = userRequest.trim();
    if (!request) {
      setError("اكتب سيناريوك باللغة الطبيعية أولاً");
      return;
    }
    if (!artifacts.fileId || !artifacts.snapshotId) {
      setError("ارفع ملفاً وشغّل تحليل الهدر أولاً");
      return;
    }
    setExecuting(true);
    setError(null);
    try {
      const body: {
        user_request: string;
        source_file_id: string;
        source_snapshot_id?: string;
        snapshot_version?: number;
        baseline_analysis_run_id?: string;
        risk_analysis_run_id?: string;
      } = {
        user_request: request,
        source_file_id: artifacts.fileId,
        baseline_analysis_run_id: artifacts.wasteRunId ?? undefined,
        risk_analysis_run_id: artifacts.riskRunId ?? undefined,
      };
      if (artifacts.snapshotId) {
        body.source_snapshot_id = artifacts.snapshotId;
      } else if (artifacts.snapshotVersion) {
        body.snapshot_version = artifacts.snapshotVersion;
      }
      const outcome = await executeAISimulation(
        auth.session.organizationId,
        auth.session.token,
        body,
      );
      writeDemoArtifacts({
        simulationRunId: outcome.simulation_run.id,
        simulationAnalysisRunId: outcome.analysis_run.id,
        lastReportId: null,
      });
      setLastRequest(outcome.user_request);
      setInterpreted(outcome.interpreted_scenario);
      setExplanation(outcome.ai_explanation);
      setFinancialReality(outcome.financial_reality ?? null);
      await loadRunResults(outcome.simulation_run.id);
      setMessage("اكتملت المحاكاة بنجاح");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setExecuting(false);
    }
  };

  React.useEffect(() => {
    if (!auth.session) return;
    if (!artifacts.simulationRunId) {
      resetRunResults();
      return;
    }
    void loadRunResults(artifacts.simulationRunId).catch(() => undefined);
    if (artifacts.simulationAnalysisRunId) {
      void hydrateFromAnalysisRun(artifacts.simulationAnalysisRunId).catch(
        () => undefined,
      );
    }
  }, [
    auth.session,
    artifacts.simulationRunId,
    artifacts.simulationAnalysisRunId,
    resetRunResults,
    loadRunResults,
    hydrateFromAnalysisRun,
  ]);

  if (auth.isLoading) return <AuthLoadingShell />;
  if (!auth.session) return null;

  const assumptionRows = [
    ...(interpreted?.actions.map((action) => ({
      label: action.description || action.action_type,
      value: [
        action.mode === "percent" && action.value != null
          ? `${action.value}%`
          : null,
        action.amount != null ? `${action.amount.toLocaleString("ar-SA")} SAR` : null,
        action.category ?? action.department ?? null,
      ]
        .filter(Boolean)
        .join(" | "),
    })) ?? []),
    ...(interpreted?.assumptions?.map((item) => ({
      label: "افتراض",
      value: item,
    })) ?? []),
  ];

  const executiveJudgment = explanation?.executive_judgment ?? null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="محاكاة الأعمال"
      subtitle={org.reportingPeriod ?? undefined}
      activeItemId="simulation"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="محاكاة السيناريوهات"
            description="صف السيناريو الذي تريد اختباره — سنحسب أثره المالي ونشرح النتائج."
            period={org.reportingPeriod}
          />

          <WorkflowIndicator activeStageId="simulation" />

          <Alert variant="default" title="إرشاد">
            {artifacts.riskRunId
              ? "سيتم ربط المحاكاة بتحليل المخاطر الحالي لتقدير أثر السيناريو على التعرّض المالي."
              : "لربط المحاكاة بالمخاطر: أكمل تحليل المخاطر أولاً ثم عد لتشغيل السيناريو."}
          </Alert>

          <section className="space-y-3">
            <label className="text-sm text-muted">سيناريوك</label>
            <Textarea
              value={userRequest}
              onChange={(event) => setUserRequest(event.target.value)}
              placeholder={SCENARIO_PLACEHOLDER}
              rows={5}
              className="min-h-[140px] resize-y"
            />
            <div className="flex flex-wrap gap-3">
              <Button disabled={executing} onClick={() => void runScenario()}>
                {executing ? "جاري التنفيذ..." : "تشغيل السيناريو"}
              </Button>
              {hasRunResults ? (
                <Button asChild variant="secondary">
                  <Link href={navRouteMap.reports}>التالي: إنشاء التقرير</Link>
                </Button>
              ) : null}
            </div>
          </section>

          {executing ? (
            <OperationLoadingPanel
              title="جاري تشغيل محاكاة السيناريو"
              description="نحلّل طلبك، نحسب الأثر المالي، ثم نعرض النتائج."
            />
          ) : null}

          {hydrating ? (
            <LoadingSkeleton className="min-h-[120px] rounded-2xl" />
          ) : null}

          {message ? <Alert variant="success" title="تم">{message}</Alert> : null}
          {error ? (
            <ErrorState
              title="تعذّر تشغيل المحاكاة"
              description={error}
              onRetry={() => setError(null)}
            />
          ) : null}

          {lastRequest ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="الطلب الأصلي" />
              <p className="rounded-2xl border border-border/60 bg-surface/40 p-4 text-sm leading-relaxed">
                {lastRequest}
              </p>
            </section>
          ) : null}

          {interpreted ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="السيناريو كما فُهم" />
              <div className="space-y-2 rounded-2xl border border-border/60 bg-surface/40 p-4">
                <p className="font-medium">{interpreted.title_ar}</p>
                <p className="text-sm text-muted">{interpreted.summary_ar}</p>
                <p className="text-xs text-muted">
                  النوع: {mapScenarioType(interpreted.scenario_type)}
                  {interpreted.target_amount != null
                    ? ` | الهدف: ${interpreted.target_amount.toLocaleString("ar-SA")} ${interpreted.currency ?? "SAR"}`
                    : null}
                  {interpreted.confidence != null
                    ? ` | الثقة: ${interpreted.confidence}%`
                    : null}
                </p>
              </div>
            </section>
          ) : null}

          {assumptionRows.length > 0 ? (
            <SimulationAssumptions assumptions={assumptionRows} />
          ) : null}

          {hasRunResults && forecast ? (
            <section className="grid gap-5 sm:grid-cols-3">
              <DashboardStatCard
                label="قبل (الأساس)"
                value={forecast.baseline}
                hint="خط الأساس"
                dense
              />
              <DashboardStatCard
                label="بعد (المتوقع)"
                value={forecast.projected}
                hint="بعد المحاكاة"
                dense
                emphasis
              />
              <DashboardStatCard
                label="الأثر المالي"
                value={forecast.delta}
                hint={forecast.confidence ?? "بدون تصنيف ثقة"}
                dense
              />
            </section>
          ) : (
            !executing && (
              <EmptyState
                title="لا توجد نتائج محاكاة بعد"
                description="اكتب سيناريوك واضغط «تشغيل السيناريو» لعرض التأثير المالي."
              />
            )
          )}

          {chartPoints.length > 0 ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="مقارنة الفترات" />
              <SimulationComparisonChart data={chartPoints} />
            </section>
          ) : null}

          {comparisons.length > 0 ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="المؤشرات الرئيسية" />
              <div className="grid gap-4 md:grid-cols-3">
                {comparisons.map((item) => (
                  <DashboardStatCard
                    key={item.name}
                    label={item.name}
                    value={item.simulated}
                    hint={`${item.current} → ${item.change}`}
                    dense
                  />
                ))}
              </div>
            </section>
          ) : null}

          {impactItems.length > 0 ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="تأثير المحاكاة حسب الفئة" />
              <SimulationImpactBreakdown items={impactItems} />
            </section>
          ) : null}

          {financialReality ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="تحليل الثقة والنطاقات" />
              <div className="grid gap-4 md:grid-cols-2">
                <InsightBlock
                  title={`مستوى الثقة: ${confidenceLabel(financialReality.confidence_level)} (${financialReality.confidence_score}/100)`}
                  body={financialReality.confidence_rationale}
                />
                {financialReality.revenue_impact ? (
                  <InsightBlock
                    title="تأثير الإيرادات (أسوأ / متوقع / أفضل)"
                    body={`${formatSar(financialReality.revenue_impact.worst)} / ${formatSar(financialReality.revenue_impact.expected)} / ${formatSar(financialReality.revenue_impact.best)}`}
                  />
                ) : null}
                <InsightBlock
                  title="تغير الإنفاق (أسوأ / متوقع / أفضل)"
                  body={`${formatSar(financialReality.expense_change.worst)} / ${formatSar(financialReality.expense_change.expected)} / ${formatSar(financialReality.expense_change.best)}`}
                />
                <InsightBlock
                  title="الأثر على السيولة (أسوأ / متوقع / أفضل)"
                  body={`${formatSar(financialReality.cash_impact.worst)} / ${formatSar(financialReality.cash_impact.expected)} / ${formatSar(financialReality.cash_impact.best)}`}
                />
              </div>
              {financialReality.action_reasonings &&
              financialReality.action_reasonings.length > 0 ? (
                <div className="mt-4 space-y-2 rounded-2xl border border-border/60 bg-surface/40 p-4">
                  <p className="text-sm font-medium">التبرير المالي</p>
                  <ul className="list-inside list-disc space-y-1 text-sm text-muted">
                    {financialReality.action_reasonings.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {financialReality.validation_notes &&
              financialReality.validation_notes.length > 0 ? (
                <Alert variant="default" title="تعديلات التحقق المالي">
                  {financialReality.validation_notes.join(" — ")}
                </Alert>
              ) : null}
            </section>
          ) : null}

          {executiveJudgment ? (
            <section className={executiveSectionSpacingClassName}>
              <SimulationExecutiveJudgment judgment={executiveJudgment} />
            </section>
          ) : null}

          {explanation ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="شرح النتائج" />
              {artifacts.riskRunId && explanation.risks ? (
                <div className="mb-4 rounded-2xl border border-warning/30 bg-warning/5 p-4">
                  <p className="mb-2 text-sm font-semibold text-black-primary">
                    كيف تؤثر المخاطر الحالية على هذا السيناريو؟
                  </p>
                  <p className="text-sm leading-relaxed text-black-primary/90">
                    {ensureExecutiveArabic(explanation.risks)}
                  </p>
                </div>
              ) : null}
              <div className="grid gap-4 md:grid-cols-2">
                <InsightBlock
                  title="الملخص التنفيذي"
                  body={ensureExecutiveArabic(explanation.executive_summary)}
                />
                <InsightBlock
                  title="الأثر المتوقع"
                  body={ensureExecutiveArabic(explanation.expected_impact)}
                />
                <InsightBlock
                  title="التغيرات المالية"
                  body={ensureExecutiveArabic(explanation.financial_changes)}
                />
                <InsightBlock
                  title="المخاطر المرتبطة"
                  body={ensureExecutiveArabic(explanation.risks)}
                />
                <InsightBlock title="الفوائد" body={ensureExecutiveArabic(explanation.benefits)} />
                <InsightBlock
                  title="التوصية للمجلس"
                  body={ensureExecutiveArabic(explanation.board_recommendation)}
                />
                <InsightBlock
                  title="الافتراضات"
                  body={ensureExecutiveArabic(explanation.assumptions)}
                />
                <InsightBlock title="مستوى الثقة" body={ensureExecutiveArabic(explanation.confidence)} />
                {explanation.forecast_ranges ? (
                  <InsightBlock
                    title="نطاقات التوقعات"
                    body={ensureExecutiveArabic(explanation.forecast_ranges)}
                  />
                ) : null}
              </div>
            </section>
          ) : null}

          {actionItems.length > 0 ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="الخطوات التالية" />
              <SimulationActionPanel items={actionItems} />
            </section>
          ) : null}
        </div>
      </PageContainer>
    </AppLayout>
  );
}

function InsightBlock({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-border/60 bg-surface/40 p-4">
      <p className="mb-2 text-sm font-medium">{title}</p>
      <p className="text-sm leading-relaxed text-muted">{body}</p>
    </div>
  );
}
