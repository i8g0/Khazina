"use client";

import * as React from "react";
import {
  BarChart3,
  FileSpreadsheet,
  PiggyBank,
  Sparkles,
  TrendingDown,
} from "lucide-react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { WasteBreakdownTable } from "@/components/waste/waste-breakdown-table";
import { WasteIdleContent } from "@/components/waste/waste-idle-content";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { PageHero } from "@/components/ui/page-hero";
import { RecommendationCard } from "@/components/ui/recommendation-card";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavGroups,
} from "@/lib/app-nav";
import type { WasteAnalysisRow } from "@/lib/placeholder-data";
import {
  useRequireAuth,
  formatApiError,
} from "@/lib/auth/auth-context";
import { useOrganizationDisplay, useOrgLookups } from "@/lib/org-lookups";
import {
  executeWasteDecision,
  generateWasteAi,
  getAiHealth,
  getWasteResult,
  listVendorFindings,
  listWasteBreakdowns,
  uploadFinancialFile,
} from "@/lib/api/khazina-api";
import { useDemoArtifacts } from "@/lib/demo/hooks";
import { beginNewFinancialDataset, writeDemoArtifacts } from "@/lib/demo/state";
import {
  formatCurrency,
  formatPercent,
  formatRecommendationDisplay,
  formatWasteCategoryName,
  mapRecommendationPriority,
} from "@/lib/format";
import { WorkflowIndicator } from "@/components/workflow/workflow-indicator";
import { AiProgressOverlay } from "@/components/workflow/ai-progress-overlay";
import { OperationLoadingPanel } from "@/components/workflow/operation-loading-panel";
import { AuthLoadingShell } from "@/components/workflow/auth-loading-shell";
import { EXECUTIVE_MESSAGES } from "@/lib/workflow/messages";
import Link from "next/link";
import { navRouteMap } from "@/lib/app-nav";
import type { RecommendationResponse } from "@/lib/api/types";
import type { WasteVendorDetail } from "@/lib/placeholder-data";

const summaryIcons = [TrendingDown, BarChart3, FileSpreadsheet, PiggyBank];

const EMPTY_SUMMARY = {
  total: null,
  wastePct: null,
  savings: null,
  opportunities: null,
} as const;

export function WastePage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const { departmentName } = useOrgLookups();
  const artifacts = useDemoArtifacts();
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const [loading, setLoading] = React.useState(false);
  const [aiLoading, setAiLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [ready, setReady] = React.useState(false);
  const [rows, setRows] = React.useState<WasteAnalysisRow[]>([]);
  const [vendorRows, setVendorRows] = React.useState<WasteVendorDetail[]>([]);
  const [recommendations, setRecommendations] = React.useState<RecommendationResponse[]>([]);
  const [summary, setSummary] = React.useState<{
    total: string | null;
    wastePct: string | null;
    savings: string | null;
    opportunities: string | null;
  }>({ ...EMPTY_SUMMARY });
  const [message, setMessage] = React.useState<string | null>(null);
  const [aiReady, setAiReady] = React.useState<boolean | null>(null);
  const [aiHealthMessage, setAiHealthMessage] = React.useState<string | null>(null);

  const resetResults = React.useCallback(() => {
    setReady(false);
    setRows([]);
    setVendorRows([]);
    setRecommendations([]);
    setSummary({ ...EMPTY_SUMMARY });
  }, []);

  const checkAiHealth = React.useCallback(async () => {
    try {
      const health = await getAiHealth();
      setAiReady(health.ollama_reachable);
      setAiHealthMessage(
        health.ollama_reachable
          ? null
          : EXECUTIVE_MESSAGES.aiUnavailable,
      );
    } catch {
      setAiReady(false);
      setAiHealthMessage(EXECUTIVE_MESSAGES.aiHealthCheckFailed);
    }
  }, []);

  React.useEffect(() => {
    void checkAiHealth();
  }, [checkAiHealth]);

  const loadResults = React.useCallback(
    async (runId: string) => {
      if (!auth.session) return;
      const [result, breakdowns, vendors] = await Promise.all([
        getWasteResult(auth.session.organizationId, auth.session.token, runId),
        listWasteBreakdowns(auth.session.organizationId, auth.session.token, runId),
        listVendorFindings(auth.session.organizationId, auth.session.token, runId),
      ]);
      setSummary({
        total: formatCurrency(result.total_waste_amount),
        wastePct: formatPercent(result.waste_percentage),
        savings:
          result.potential_savings_amount != null
            ? formatCurrency(result.potential_savings_amount)
            : null,
        opportunities:
          result.active_savings_opportunities != null
            ? String(result.active_savings_opportunities)
            : null,
      });
      setRows(
        breakdowns.map((item) => ({
          id: item.id,
          category: formatWasteCategoryName(item.category_name),
          amount: item.amount,
          percentage: formatPercent(item.percentage),
          department: item.department_id
            ? departmentName(item.department_id) ?? ""
            : "",
        })),
      );
      setVendorRows(
        vendors.map((item) => ({
          id: item.id,
          vendor: item.vendor_name,
          category: item.category_label ?? "غير مصنّف",
          amount: item.amount,
          deviation: item.deviation_label ?? "غير متوفر",
          status: item.status,
        })),
      );
      setReady(true);
    },
    [auth.session, departmentName],
  );

  React.useEffect(() => {
    if (!auth.session) return;
    if (!artifacts.wasteRunId) {
      resetResults();
      return;
    }
    setLoading(true);
    setError(null);
    void loadResults(artifacts.wasteRunId)
      .catch((err) => setError(formatApiError(err)))
      .finally(() => setLoading(false));
  }, [auth.session, artifacts.wasteRunId, loadResults, resetResults]);

  const runPipeline = async (file?: File) => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    setMessage(null);
    setRecommendations([]);
    try {
      let current = artifacts;
      if (file) {
        const upload = await uploadFinancialFile(
          auth.session.organizationId,
          auth.session.token,
          file,
        );
        if (!upload.financial_snapshot) {
          throw new Error("فشل إنشاء اللقطة المالية");
        }
        current = beginNewFinancialDataset({
          fileId: upload.financial_file.id,
          snapshotId: upload.financial_snapshot.id,
          snapshotVersion: upload.financial_snapshot.snapshot_version,
        });
        resetResults();
      }
      if (!current.fileId || !current.snapshotId || !current.snapshotVersion) {
        throw new Error("ارفع ملفاً من مستودع البيانات أولاً");
      }
      const decisionBody: {
        title: string;
        source_file_id: string;
        source_snapshot_id?: string;
        snapshot_version?: number;
      } = {
        title: "تحليل هدر مالي",
        source_file_id: current.fileId,
        source_snapshot_id: current.snapshotId,
      };
      const decision = await executeWasteDecision(
        auth.session.organizationId,
        auth.session.token,
        decisionBody,
      );
      writeDemoArtifacts({
        wasteRunId: decision.analysis_run.id,
        aiRecommendationsReady: false,
      });
      await loadResults(decision.analysis_run.id);
      setMessage("اكتمل تحليل الهدر بنجاح");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const runAi = async () => {
    if (!auth.session) return;
    const runId = artifacts.wasteRunId;
    if (!runId) {
      setError("شغّل تحليل الهدر أولاً");
      return;
    }
    setAiLoading(true);
    setError(null);
    try {
      const health = await getAiHealth();
      if (!health.ollama_reachable) {
        setAiReady(false);
        setAiHealthMessage(EXECUTIVE_MESSAGES.aiUnavailable);
        throw new Error(EXECUTIVE_MESSAGES.aiUnavailable);
      }
      setAiReady(true);
      setAiHealthMessage(null);
      const outcome = await generateWasteAi(
        auth.session.organizationId,
        auth.session.token,
        runId,
      );
      setRecommendations(outcome.recommendations);
      writeDemoArtifacts({ aiRecommendationsReady: true });
      setMessage(`تم توليد ${outcome.recommendation_count} توصية بالذكاء الاصطناعي`);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setAiLoading(false);
    }
  };

  const handleFilePick = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (file) {
      void runPipeline(file);
    }
  };

  if (auth.isLoading) return <AuthLoadingShell />;
  if (!auth.session) return null;

  const hasUploadedFile = Boolean(artifacts.fileId);

  const kpis = [
    { label: "إجمالي الهدر", value: summary.total, hint: "من محرك القرار" },
    { label: "نسبة الهدر", value: summary.wastePct, hint: "من الإنفاق" },
    {
      label: "التوفير المحتمل",
      value: summary.savings,
      hint: summary.savings ? "فرص الادخار" : "لم يُسجَّل توفير محتمل",
    },
    {
      label: "فرص الادخار",
      value: summary.opportunities,
      hint: summary.opportunities ? "نشطة من التحليل" : "لم تُسجَّل فرص بعد",
    },
  ];

  const aiBlocked = aiReady === false;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="كشف الهدر"
      subtitle={org.reportingPeriod ?? undefined}
      activeItemId="waste"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="كشف الهدر المالي"
            description="تحليل أنماط الهدر المالي وتوليد توصيات تنفيذية مبنية على بياناتك."
            period={org.reportingPeriod}
          />

          <WorkflowIndicator activeStageId={ready && !artifacts.aiRecommendationsReady ? "ai" : "waste"} />

          <AiProgressOverlay open={aiLoading} />

          <div className="space-y-2">
            <div className="flex flex-wrap gap-3">
              <Button disabled={loading} onClick={() => void runPipeline()}>
                {loading ? "جاري التحليل..." : "تشغيل تحليل الهدر"}
              </Button>
              <Button
                variant="secondary"
                disabled={loading}
                onClick={() => fileInputRef.current?.click()}
              >
                رفع سريع وتحليل
              </Button>
              <Button
                variant="secondary"
                disabled={aiLoading || !ready || aiBlocked}
                onClick={() => void runAi()}
              >
                <Sparkles className="h-4 w-4" />
                {aiLoading ? "جاري توليد التوصيات..." : "توليد توصيات الذكاء الاصطناعي"}
              </Button>
              {ready && artifacts.aiRecommendationsReady ? (
                <Button asChild variant="secondary">
                  <Link href={navRouteMap.simulation}>التالي: محاكاة السيناريو</Link>
                </Button>
              ) : null}
            </div>
            <p className="text-sm text-muted">
              {hasUploadedFile
                ? "الملف النشط جاهز — استخدم «تشغيل تحليل الهدر» للمتابعة. للرفع الأول، يُفضّل "
                : "للبدء، ارفع ملفك من "}
              {!hasUploadedFile ? (
                <Link href={navRouteMap.data} className="font-medium text-gold-dark underline-offset-2 hover:underline">
                  مستودع البيانات
                </Link>
              ) : (
                <Link href={navRouteMap.data} className="font-medium text-gold-dark underline-offset-2 hover:underline">
                  مستودع البيانات
                </Link>
              )}
              {hasUploadedFile
                ? "."
                : " — «رفع سريع وتحليل» للمستخدمين المتقدمين فقط."}
            </p>
            {!hasUploadedFile ? (
              <p className="text-xs text-muted">{EXECUTIVE_MESSAGES.uploadQuickHint}</p>
            ) : null}
          </div>

          {aiHealthMessage && !ready ? (
            <Alert variant="warning" title="الذكاء الاصطناعي">
              {aiHealthMessage}
            </Alert>
          ) : null}

          {message ? <Alert variant="success" title="تم">{message}</Alert> : null}
          {error ? (
            <ErrorState
              title="تعذّر إكمال العملية"
              description={error}
              onRetry={() => setError(null)}
            />
          ) : null}

          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls,.csv"
            className="hidden"
            onChange={handleFilePick}
          />

          {!ready && !loading ? (
            <WasteIdleContent
              onUploadClick={() => fileInputRef.current?.click()}
              preferDataManagement={!hasUploadedFile}
            />
          ) : null}

          {loading ? (
            <OperationLoadingPanel
              title="جاري تشغيل محرك تحليل الهدر"
              description="تحليل أنماط الهدر في البيانات المالية — عادةً يستغرق ثوانٍ قليلة."
            />
          ) : ready ? (
            <>
              <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
                {kpis.map((kpi, index) => {
                  const Icon = summaryIcons[index];
                  return (
                    <DashboardStatCard
                      key={kpi.label}
                      label={kpi.label}
                      value={
                        kpi.value ?? (
                          <span className="text-sm font-normal text-muted">
                            غير متوفر في نتائج التحليل
                          </span>
                        )
                      }
                      hint={kpi.hint}
                      emphasis
                      dense
                      icon={<Icon className="h-[17px] w-[17px]" strokeWidth={1.75} />}
                    />
                  );
                })}
              </section>

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader dense title="تفصيل الفئات والموردين" />
                <WasteBreakdownTable analysisRows={rows} vendorRows={vendorRows} />
              </section>

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader dense title="توصيات الذكاء الاصطناعي" />
                {aiHealthMessage && aiBlocked ? (
                  <EmptyState
                    title="الذكاء الاصطناعي غير جاهز"
                    description={aiHealthMessage}
                  />
                ) : recommendations.length === 0 ? (
                  <EmptyState
                    title="لا توجد توصيات بعد"
                    description="اضغط «توليد توصيات الذكاء الاصطناعي» لإنشاء توصيات مبنية على نتائج هذا التحليل."
                  />
                ) : (
                  <div className="grid gap-4 md:grid-cols-2">
                    {recommendations.map((rec) => {
                      const display = formatRecommendationDisplay(rec);
                      return (
                        <RecommendationCard
                          key={rec.id}
                          title={display.title}
                          description={display.description}
                          badge={mapRecommendationPriority(rec.priority)}
                        />
                      );
                    })}
                  </div>
                )}
              </section>
            </>
          ) : null}
        </div>
      </PageContainer>
    </AppLayout>
  );
}
