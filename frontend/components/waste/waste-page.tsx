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
import { ErrorState } from "@/components/ui/error-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PageHero } from "@/components/ui/page-hero";
import { RecommendationCard } from "@/components/ui/recommendation-card";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavItems,
} from "@/lib/app-nav";
import { organization } from "@/lib/placeholder-data";
import type { WasteAnalysisRow } from "@/lib/placeholder-data";
import { useRequireAuth, formatApiError } from "@/lib/auth/auth-context";
import {
  executeWasteDecision,
  generateWasteAi,
  getWasteResult,
  listWasteBreakdowns,
  uploadFinancialFile,
} from "@/lib/api/khazina-api";
import { readDemoArtifacts, writeDemoArtifacts } from "@/lib/demo/state";
import { formatCurrency, formatPercent } from "@/lib/format";
import type { RecommendationResponse } from "@/lib/api/types";

const summaryIcons = [TrendingDown, BarChart3, FileSpreadsheet, PiggyBank];

export function WastePage() {
  const auth = useRequireAuth();
  const [loading, setLoading] = React.useState(false);
  const [aiLoading, setAiLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [ready, setReady] = React.useState(false);
  const [rows, setRows] = React.useState<WasteAnalysisRow[]>([]);
  const [recommendations, setRecommendations] = React.useState<RecommendationResponse[]>([]);
  const [summary, setSummary] = React.useState({
    total: "—",
    wastePct: "—",
    savings: "—",
    opportunities: "—",
  });
  const [message, setMessage] = React.useState<string | null>(null);

  const loadResults = React.useCallback(
    async (runId: string) => {
      if (!auth.session) return;
      const [result, breakdowns] = await Promise.all([
        getWasteResult(auth.session.organizationId, auth.session.token, runId),
        listWasteBreakdowns(auth.session.organizationId, auth.session.token, runId),
      ]);
      setSummary({
        total: formatCurrency(result.total_waste_amount),
        wastePct: formatPercent(result.waste_percentage),
        savings: formatCurrency(result.potential_savings_amount ?? 0),
        opportunities: String(result.active_savings_opportunities ?? 0),
      });
      setRows(
        breakdowns.map((item, index) => ({
          id: item.id,
          category: item.category_name,
          amount: item.amount,
          percentage: formatPercent(item.percentage),
          department: "المشتريات",
        })),
      );
      setReady(true);
    },
    [auth.session],
  );

  React.useEffect(() => {
    const artifacts = readDemoArtifacts();
    if (auth.session && artifacts.wasteRunId) {
      setLoading(true);
      void loadResults(artifacts.wasteRunId)
        .catch((err) => setError(formatApiError(err)))
        .finally(() => setLoading(false));
    }
  }, [auth.session, loadResults]);

  const runPipeline = async (file?: File) => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      let artifacts = readDemoArtifacts();
      if (file) {
        const upload = await uploadFinancialFile(
          auth.session.organizationId,
          auth.session.token,
          file,
        );
        if (!upload.financial_snapshot) {
          throw new Error("فشل إنشاء اللقطة المالية");
        }
        artifacts = writeDemoArtifacts({
          fileId: upload.financial_file.id,
          snapshotId: upload.financial_snapshot.id,
          snapshotVersion: upload.financial_snapshot.snapshot_version,
        });
      }
      if (!artifacts.fileId || !artifacts.snapshotId || !artifacts.snapshotVersion) {
        throw new Error("ارفع ملفاً من مستودع البيانات أولاً");
      }
      const decision = await executeWasteDecision(
        auth.session.organizationId,
        auth.session.token,
        {
          title: "تحليل هدر — Procurement_Q2",
          source_file_id: artifacts.fileId,
          source_snapshot_id: artifacts.snapshotId,
          snapshot_version: artifacts.snapshotVersion,
        },
      );
      writeDemoArtifacts({ wasteRunId: decision.analysis_run.id });
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
    const runId = readDemoArtifacts().wasteRunId;
    if (!runId) {
      setError("شغّل تحليل الهدر أولاً");
      return;
    }
    setAiLoading(true);
    setError(null);
    try {
      const outcome = await generateWasteAi(
        auth.session.organizationId,
        auth.session.token,
        runId,
      );
      setRecommendations(outcome.recommendations);
      setMessage(`تم توليد ${outcome.recommendation_count} توصية بالذكاء الاصطناعي`);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setAiLoading(false);
    }
  };

  if (!auth.session) return null;

  const kpis = [
    { label: "إجمالي الهدر", value: summary.total, hint: "من محرك القرار" },
    { label: "نسبة الهدر", value: summary.wastePct, hint: "من الإنفاق" },
    { label: "التوفير المحتمل", value: summary.savings, hint: "فرص الادخار" },
    { label: "فرص الادخار", value: summary.opportunities, hint: "نشطة" },
  ];

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="كشف الهدر"
      subtitle={organization.reportingPeriod}
      activeItemId="waste"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="كشف الهدر المالي"
            description="رفع البيانات وتشغيل محرك القرار وتوليد التوصيات التنفيذية."
            period={organization.reportingPeriod}
          />

          <div className="flex flex-wrap gap-3">
            <Button disabled={loading} onClick={() => void runPipeline()}>
              تشغيل تحليل الهدر
            </Button>
            <Button variant="secondary" disabled={aiLoading || !ready} onClick={() => void runAi()}>
              <Sparkles className="h-4 w-4" />
              {aiLoading ? "جاري توليد التوصيات..." : "توليد توصيات الذكاء الاصطناعي"}
            </Button>
          </div>

          {message ? <Alert variant="success" title="تم">{message}</Alert> : null}
          {error ? <ErrorState title="خطأ" description={error} onRetry={() => setError(null)} /> : null}

          {!ready && !loading ? <WasteIdleContent onUploadClick={() => void runPipeline()} /> : null}

          {loading ? (
            <LoadingSkeleton className="min-h-[320px] rounded-2xl" />
          ) : ready ? (
            <>
              <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
                {kpis.map((kpi, index) => {
                  const Icon = summaryIcons[index];
                  return (
                    <DashboardStatCard
                      key={kpi.label}
                      label={kpi.label}
                      value={kpi.value}
                      hint={kpi.hint}
                      emphasis
                      dense
                      icon={<Icon className="h-[17px] w-[17px]" strokeWidth={1.75} />}
                    />
                  );
                })}
              </section>

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader dense title="تفصيل الفئات" />
                <WasteBreakdownTable analysisRows={rows} vendorRows={[]} />
              </section>

              {recommendations.length > 0 ? (
                <section className={executiveSectionSpacingClassName}>
                  <DashboardSectionHeader dense title="توصيات الذكاء الاصطناعي" />
                  <div className="grid gap-4 md:grid-cols-2">
                    {recommendations.map((rec) => (
                      <RecommendationCard
                        key={rec.id}
                        title={rec.title}
                        description={rec.description}
                        badge={rec.priority}
                      />
                    ))}
                  </div>
                </section>
              ) : null}
            </>
          ) : null}
        </div>
      </PageContainer>
    </AppLayout>
  );
}
