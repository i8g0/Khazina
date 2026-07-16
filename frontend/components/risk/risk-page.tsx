"use client";

import * as React from "react";
import {
  AlertTriangle,
  BarChart3,
  ClipboardList,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import Link from "next/link";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { RiskActiveTable } from "@/components/risk/risk-active-table";
import { RiskAiSummary } from "@/components/risk/risk-ai-summary";
import { RiskAnalysesTable } from "@/components/risk/risk-analyses-table";
import { RiskCharts } from "@/components/risk/risk-charts";
import { RiskFindingsTable } from "@/components/risk/risk-findings-table";
import { RiskIdleContent } from "@/components/risk/risk-idle-content";
import { RiskMitigationPlans } from "@/components/risk/risk-mitigation-plans";
import { RiskPriorityMatrix } from "@/components/risk/risk-priority-matrix";
import { RiskRecommendationCard } from "@/components/risk/risk-recommendation-card";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PageHero } from "@/components/ui/page-hero";
import { AiProgressOverlay } from "@/components/workflow/ai-progress-overlay";
import { AuthLoadingShell } from "@/components/workflow/auth-loading-shell";
import { OperationLoadingPanel } from "@/components/workflow/operation-loading-panel";
import { WorkflowIndicator } from "@/components/workflow/workflow-indicator";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavGroups,
  navRouteMap,
} from "@/lib/app-nav";
import {
  executeRiskAnalysis,
  generateRiskAi,
  getAiHealth,
  getRiskAnalysis,
  getRiskResult,
  listMitigationPlans,
  listRecommendations,
  listRiskAnalyses,
  listRiskFindings,
  listRisks,
  promoteRiskFinding,
  reviewRiskFinding,
} from "@/lib/api/khazina-api";
import type {
  RiskAnalysisResultResponse,
  RiskFindingResponse,
  RiskResponse,
} from "@/lib/api/types";
import {
  useRequireAuth,
  formatApiError,
} from "@/lib/auth/auth-context";
import { useDemoArtifacts } from "@/lib/demo/hooks";
import { writeDemoArtifacts } from "@/lib/demo/state";
import {
  parseExecutiveRecommendation,
  mapRiskPosture,
} from "@/lib/format";
import {
  buildCategoryChart,
  buildDepartmentChart,
  buildMatrixItems,
  buildSeverityChart,
  countActiveRisks,
  countCriticalRisks,
  mapAnalysisRunToHistory,
  mapFindingToView,
  mapMitigationPlan,
  mapRecommendation,
  mapRiskToItemView,
} from "@/lib/risk/mappers";
import type {
  RiskAnalysisHistoryItem,
  RiskFindingView,
  RiskItemView,
  RiskMitigationPlanView,
  RiskRecommendationView,
} from "@/lib/risk/view-types";
import { useOrganizationDisplay, useOrgLookups } from "@/lib/org-lookups";
import { EXECUTIVE_MESSAGES } from "@/lib/workflow/messages";

const kpiIcons = [ShieldAlert, AlertTriangle, BarChart3, ClipboardList];

export function RiskPage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const { departmentName } = useOrgLookups();
  const artifacts = useDemoArtifacts();

  const [loading, setLoading] = React.useState(false);
  const [aiLoading, setAiLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [ready, setReady] = React.useState(false);
  const [busyFindingId, setBusyFindingId] = React.useState<string | null>(null);
  const [aiReady, setAiReady] = React.useState<boolean | null>(null);
  const [aiHealthMessage, setAiHealthMessage] = React.useState<string | null>(null);

  const [result, setResult] = React.useState<RiskAnalysisResultResponse | null>(null);
  const [rawFindings, setRawFindings] = React.useState<RiskFindingResponse[]>([]);
  const [findings, setFindings] = React.useState<RiskFindingView[]>([]);
  const [registerRisks, setRegisterRisks] = React.useState<RiskResponse[]>([]);
  const [registerRows, setRegisterRows] = React.useState<RiskItemView[]>([]);
  const [history, setHistory] = React.useState<RiskAnalysisHistoryItem[]>([]);
  const [mitigationPlans, setMitigationPlans] = React.useState<RiskMitigationPlanView[]>([]);
  const [recommendations, setRecommendations] = React.useState<RiskRecommendationView[]>([]);
  const [aiInsights, setAiInsights] = React.useState<Record<string, unknown> | null>(null);

  const checkAiHealth = React.useCallback(async () => {
    try {
      const health = await getAiHealth();
      setAiReady(health.ollama_reachable);
      setAiHealthMessage(
        health.ollama_reachable ? null : EXECUTIVE_MESSAGES.aiUnavailable,
      );
    } catch {
      setAiReady(false);
      setAiHealthMessage(EXECUTIVE_MESSAGES.aiHealthCheckFailed);
    }
  }, []);

  React.useEffect(() => {
    void checkAiHealth();
  }, [checkAiHealth]);

  const loadRegisterAndHistory = React.useCallback(async () => {
    if (!auth.session) return [];
    const [risks, runs, plans] = await Promise.all([
      listRisks(auth.session.organizationId, auth.session.token, { limit: 50 }),
      listRiskAnalyses(auth.session.organizationId, auth.session.token, { limit: 20 }),
      listMitigationPlans(auth.session.organizationId, auth.session.token, { limit: 20 }),
    ]);
    const riskNameById = new Map(risks.map((r) => [r.id, r.name]));
    setRegisterRisks(risks);
    setRegisterRows(risks.map((r) => mapRiskToItemView(r, departmentName)));
    setMitigationPlans(plans.map((p) => mapMitigationPlan(p, riskNameById)));
    setHistory(runs.map((run) => mapAnalysisRunToHistory(run)));
    return risks;
  }, [auth.session, departmentName]);

  const loadRunResults = React.useCallback(
    async (runId: string) => {
      if (!auth.session) return;
      const [runDetail, runResult, runFindings, recs] = await Promise.all([
        getRiskAnalysis(auth.session.organizationId, auth.session.token, runId),
        getRiskResult(auth.session.organizationId, auth.session.token, runId),
        listRiskFindings(auth.session.organizationId, auth.session.token, runId, {
          limit: 100,
        }),
        listRecommendations(auth.session.organizationId, auth.session.token, {
          domain_source: "risk",
          limit: 20,
        }),
      ]);
      setResult(runResult);
      setRawFindings(runFindings);
      setFindings(runFindings.map((f) => mapFindingToView(f, departmentName)));
      const insights = runDetail.analysis_run.runtime_metadata?.ai_insights;
      if (insights && typeof insights === "object") {
        setAiInsights(insights as Record<string, unknown>);
      }
      setRecommendations(
        recs.filter((r) => r.analysis_run_id === runId).map(mapRecommendation),
      );
      setReady(true);
    },
    [auth.session, departmentName],
  );

  const refreshAll = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    try {
      await loadRegisterAndHistory();
      if (artifacts.riskRunId) {
        await loadRunResults(artifacts.riskRunId);
      }
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session, artifacts.riskRunId, loadRegisterAndHistory, loadRunResults]);

  React.useEffect(() => {
    void refreshAll();
  }, [refreshAll]);

  const runAnalysis = async () => {
    if (!auth.session) return;
    if (!artifacts.fileId || !artifacts.snapshotId) {
      setError("ارفع ملفاً من مركز البيانات المالية أولاً");
      return;
    }
    setLoading(true);
    setError(null);
    setMessage(null);
    setAiInsights(null);
    setRecommendations([]);
    try {
      const outcome = await executeRiskAnalysis(
        auth.session.organizationId,
        auth.session.token,
        {
          title: "تحليل المخاطر المالية",
          source_file_id: artifacts.fileId,
          source_snapshot_id: artifacts.snapshotId,
        },
      );
      writeDemoArtifacts({
        riskRunId: outcome.analysis_run.id,
        riskAiReady: false,
        lastReportId: null,
      });
      await loadRunResults(outcome.analysis_run.id);
      await loadRegisterAndHistory();
      setMessage("اكتمل تحليل المخاطر بنجاح");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const runAi = async () => {
    if (!auth.session || !artifacts.riskRunId) {
      setError("شغّل تحليل المخاطر أولاً");
      return;
    }
    setAiLoading(true);
    setError(null);
    try {
      if (aiReady === false) {
        throw new Error(aiHealthMessage ?? EXECUTIVE_MESSAGES.aiUnavailable);
      }
      const outcome = await generateRiskAi(
        auth.session.organizationId,
        auth.session.token,
        artifacts.riskRunId,
      );
      setAiInsights(outcome.ai_insights);
      setRecommendations(outcome.recommendations.map(mapRecommendation));
      writeDemoArtifacts({ riskAiReady: true });
      setMessage(`تم إعداد ${outcome.recommendation_count} توصية للمخاطر`);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setAiLoading(false);
    }
  };

  const handleReview = async (findingId: string, action: string) => {
    if (!auth.session) return;
    setBusyFindingId(findingId);
    setError(null);
    try {
      await reviewRiskFinding(
        auth.session.organizationId,
        auth.session.token,
        findingId,
        { action },
      );
      if (artifacts.riskRunId) {
        await loadRunResults(artifacts.riskRunId);
      }
      setMessage("تم تسجيل إجراء المراجعة");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setBusyFindingId(null);
    }
  };

  const handlePromote = async (findingId: string) => {
    if (!auth.session) return;
    setBusyFindingId(findingId);
    setError(null);
    try {
      await promoteRiskFinding(
        auth.session.organizationId,
        auth.session.token,
        findingId,
        {},
      );
      await loadRegisterAndHistory();
      if (artifacts.riskRunId) {
        await loadRunResults(artifacts.riskRunId);
      }
      setMessage("تمت ترقية النتيجة إلى سجل المخاطر");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setBusyFindingId(null);
    }
  };

  if (auth.isLoading) return <AuthLoadingShell />;
  if (!auth.session) return null;

  const hasFile = Boolean(artifacts.fileId);
  const showIdle =
    !loading && !ready && !artifacts.riskRunId && registerRows.length === 0;

  const activeCount = countActiveRisks(registerRisks);
  const criticalCount = countCriticalRisks(registerRisks, result);

  const kpis = [
    {
      label: "المخاطر النشطة",
      value: activeCount > 0 ? String(activeCount) : result ? String(result.total_findings) : null,
      hint: "من سجل المخاطر",
    },
    {
      label: "المخاطر الحرجة",
      value: criticalCount > 0 ? String(criticalCount) : null,
      hint: "أولوية عالية",
    },
    {
      label: "الوضع العام",
      value: result ? mapRiskPosture(result.overall_posture_level) : null,
      hint: "من آخر تقييم للمخاطر",
    },
    {
      label: "نتائج التحليل",
      value: result ? String(result.total_findings) : null,
      hint: "من آخر تشغيل",
    },
  ];

  const severityChart = result ? buildSeverityChart(result) : [];
  const categoryChart = rawFindings.length ? buildCategoryChart(rawFindings) : [];
  const departmentChart = registerRisks.length
    ? buildDepartmentChart(registerRisks, departmentName)
    : [];
  const matrixItems = rawFindings.length ? buildMatrixItems(rawFindings) : [];

  const aiBlocked = aiReady === false;
  const hasChartData =
    severityChart.some((x) => x.count > 0) || departmentChart.length > 0;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="إدارة المخاطر"
      subtitle={org.reportingPeriod ?? undefined}
      activeItemId="risk"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="إدارة المخاطر"
            description="متابعة وتحليل المخاطر التشغيلية والمالية للمؤسسة."
            period={org.reportingPeriod}
          />

          <WorkflowIndicator />

          {message ? <Alert variant="success">{message}</Alert> : null}
          {error ? (
            <ErrorState
              title="تعذّر إكمال العملية"
              description={error}
              onRetry={() => void refreshAll()}
            />
          ) : null}

          <section className="flex flex-wrap gap-3">
            <Button onClick={() => void runAnalysis()} disabled={loading || !hasFile}>
              تشغيل تحليل المخاطر
            </Button>
            <Button
              variant="outline"
              onClick={() => void runAi()}
              disabled={aiLoading || !artifacts.riskRunId || aiBlocked}
            >
              <Sparkles className="ms-2 h-4 w-4" />
              إعداد ملخص المخاطر
            </Button>
            {!hasFile ? (
              <Button variant="ghost" asChild>
                <Link href={navRouteMap.data}>مركز البيانات المالية</Link>
              </Button>
            ) : null}
          </section>

          {aiHealthMessage ? (
            <Alert variant="warning">{aiHealthMessage}</Alert>
          ) : null}

          {(loading || aiLoading) && (
            <OperationLoadingPanel
              title={aiLoading ? "جاري توليد الملخص..." : "جاري تحميل بيانات المخاطر..."}
            />
          )}
          {aiLoading ? <AiProgressOverlay open={aiLoading} /> : null}

          {showIdle ? (
            <RiskIdleContent
              hasUploadedFile={hasFile}
              onRunAnalysis={() => void runAnalysis()}
            />
          ) : null}

          <section className="space-y-3">
            <DashboardSectionHeader dense title="مؤشرات المخاطر" />
            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
              {kpiIcons.map((Icon, index) => (
                <DashboardStatCard
                  key={kpis[index].label}
                  label={kpis[index].label}
                  value={
                    kpis[index].value ?? (
                      <span className="text-sm font-normal text-muted">—</span>
                    )
                  }
                  hint={kpis[index].hint}
                  emphasis
                  dense
                  icon={<Icon className="h-[17px] w-[17px]" strokeWidth={1.75} />}
                />
              ))}
            </div>
          </section>

          {aiInsights ? (
            <RiskAiSummary
              executiveSummary={
                typeof aiInsights.risk_executive_summary === "string"
                  ? aiInsights.risk_executive_summary
                  : null
              }
              executiveBrief={
                typeof aiInsights.risk_executive_brief === "string"
                  ? aiInsights.risk_executive_brief
                  : null
              }
              explanation={
                typeof aiInsights.risk_explanation === "string"
                  ? aiInsights.risk_explanation
                  : null
              }
              boardReport={
                typeof aiInsights.risk_board_report === "string"
                  ? aiInsights.risk_board_report
                  : null
              }
            />
          ) : null}

          {loading && !ready ? (
            <LoadingSkeleton className="min-h-[360px] rounded-2xl" />
          ) : hasChartData ? (
            <RiskCharts
              bySeverity={severityChart}
              byDepartment={departmentChart}
              byCategory={categoryChart}
            />
          ) : (
            <EmptyState
              title="لا توجد بيانات للرسوم"
              description="شغّل تحليل المخاطر أو سجّل مخاطر في السجل"
            />
          )}

          {matrixItems.length > 0 ? (
            <RiskPriorityMatrix items={matrixItems} />
          ) : null}

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader dense title="مراجعة النتائج" />
            {findings.length === 0 ? (
              <EmptyState
                title="لا توجد نتائج للمراجعة"
                description="ستظهر النتائج بعد تشغيل تحليل المخاطر"
              />
            ) : (
              <RiskFindingsTable
                findings={findings}
                onReview={(id, action) => void handleReview(id, action)}
                onPromote={(id) => void handlePromote(id)}
                busyFindingId={busyFindingId}
              />
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader dense title="سجل المخاطر" />
            {registerRows.length === 0 ? (
              <EmptyState
                title="السجل فارغ"
                description="رقِّ النتائج المعتمدة إلى سجل المخاطر المؤسسي"
              />
            ) : (
              <RiskActiveTable data={registerRows} />
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader dense title="سجل التحليلات" />
            {history.length === 0 ? (
              <EmptyState title="لا توجد تحليلات" description="لم يُنفَّذ أي تحليل مخاطر بعد" />
            ) : (
              <RiskAnalysesTable data={history} />
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader dense title="توصيات التخفيف" />
            {recommendations.length === 0 ? (
              <EmptyState
                title="لا توجد توصيات"
                description="ولّد ملخص المخاطر بعد اكتمال التحليل"
              />
            ) : (
              <div className="grid gap-5 lg:grid-cols-3">
                {recommendations.map((item) => {
                  const display = parseExecutiveRecommendation({
                    title: item.title,
                    description: item.description,
                    source_context: item.source_context as Record<string, unknown> | null,
                  });
                  return (
                    <RiskRecommendationCard
                      key={item.id}
                      item={{
                        ...item,
                        title: display.title,
                        description: display.description,
                      }}
                    />
                  );
                })}
              </div>
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader dense title="خطط التخفيف" />
            {mitigationPlans.length === 0 ? (
              <EmptyState title="لا توجد خطط" description="لا توجد خطط تخفيف مسجّلة" />
            ) : (
              <RiskMitigationPlans plans={mitigationPlans} />
            )}
          </section>
        </div>
      </PageContainer>
    </AppLayout>
  );
}
