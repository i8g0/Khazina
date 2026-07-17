"use client";

import * as React from "react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardAnalysesTable } from "@/components/dashboard/dashboard-analyses-table";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { ExecutiveAlertsPanel } from "@/components/dashboard/executive-alerts-panel";
import { ExecutiveBriefPanel } from "@/components/dashboard/executive-brief-panel";
import { ExecutiveDecisionPipeline } from "@/components/dashboard/executive-decision-pipeline";
import { ExecutiveHealthBanner } from "@/components/dashboard/executive-health-banner";
import { ExecutiveIndicatorGrid } from "@/components/dashboard/executive-indicator-grid";
import { ExecutiveStoryTimeline } from "@/components/dashboard/executive-story-timeline";
import { ExecutiveWasteChart } from "@/components/dashboard/executive-waste-chart";
import { DashboardRecommendationCard } from "@/components/dashboard/dashboard-recommendation-card";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { AuthLoadingShell } from "@/components/workflow/auth-loading-shell";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { executivePageContainerClassName, getAppNavGroups, navRouteMap } from "@/lib/app-nav";
import { DEMO_ARTIFACTS_CHANGED } from "@/lib/demo/state";
import { buildExecutiveCommandCenter } from "@/lib/dashboard/build-command-center";
import type { ExecutiveCommandCenterModel } from "@/lib/dashboard/command-center-types";
import type { RecentAnalysis } from "@/lib/placeholder-data";
import { useRequireAuth, formatApiError } from "@/lib/auth/auth-context";
import { useOrganizationDisplay, useOrgLookups } from "@/lib/org-lookups";
import {
  getRiskResult,
  getWasteResult,
  listRecentAnalyses,
  listRecommendations,
  listReports,
  listRisks,
  listVendorFindings,
  listWasteBreakdowns,
} from "@/lib/api/khazina-api";
import {
  formatDate,
  formatRecommendationDisplay,
  mapAnalysisType,
  mapRecommendationPriority,
  mapRunStatus,
} from "@/lib/format";

const dashboardPageSpacingClassName = "space-y-[2.75rem] md:space-y-[3.25rem]";
const dashboardSectionSpacingClassName = "space-y-4 md:space-y-5";

function latestCompletedRun(
  runs: Awaited<ReturnType<typeof listRecentAnalyses>>,
  types: string[],
) {
  return runs.find(
    (run) => types.includes(run.analysis_type) && run.status === "completed",
  );
}

export function DashboardPage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const { departmentName, fileName } = useOrgLookups();
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [commandCenter, setCommandCenter] =
    React.useState<ExecutiveCommandCenterModel | null>(null);
  const [analyses, setAnalyses] = React.useState<RecentAnalysis[]>([]);
  const [recommendations, setRecommendations] = React.useState<
    { id: string; title: string; description: string; badge: string; confidence: string }[]
  >([]);

  const load = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    try {
      const [runs, recs, risks, reports] = await Promise.all([
        listRecentAnalyses(auth.session.organizationId, auth.session.token),
        listRecommendations(auth.session.organizationId, auth.session.token),
        listRisks(auth.session.organizationId, auth.session.token, { limit: 50 }),
        listReports(auth.session.organizationId, auth.session.token),
      ]);

      const wasteRun = latestCompletedRun(runs, ["financial_waste", "waste"]);
      const riskRun = latestCompletedRun(runs, ["risk"]);

      const [wasteResult, wasteBreakdowns, vendors, riskResult] = await Promise.all([
        wasteRun
          ? getWasteResult(
              auth.session.organizationId,
              auth.session.token,
              wasteRun.id,
            ).catch(() => null)
          : Promise.resolve(null),
        wasteRun
          ? listWasteBreakdowns(
              auth.session.organizationId,
              auth.session.token,
              wasteRun.id,
            ).catch(() => [])
          : Promise.resolve([]),
        wasteRun
          ? listVendorFindings(
              auth.session.organizationId,
              auth.session.token,
              wasteRun.id,
              { limit: 10 },
            ).catch(() => [])
          : Promise.resolve([]),
        riskRun
          ? getRiskResult(
              auth.session.organizationId,
              auth.session.token,
              riskRun.id,
            ).catch(() => null)
          : Promise.resolve(null),
      ]);

      setAnalyses(
        runs.slice(0, 5).map((run) => ({
          id: run.id,
          title: run.title,
          type: mapAnalysisType(run.analysis_type),
          sourceFile: run.source_file_id
            ? fileName(run.source_file_id) ?? "ملف غير معروف"
            : "لا يوجد ملف مصدر",
          date: run.completed_at ? formatDate(run.completed_at) : "لم يكتمل بعد",
          status: mapRunStatus(run.status),
        })),
      );

      setRecommendations(
        recs.slice(0, 3).map((rec) => ({
          id: rec.id,
          title: rec.title,
          description: rec.description,
          badge: mapRecommendationPriority(rec.priority),
          confidence: rec.confidence_label ?? "بدون تصنيف ثقة",
        })),
      );

      setCommandCenter(
        buildExecutiveCommandCenter({
          runs,
          recommendations: recs,
          risks,
          wasteResult,
          wasteBreakdowns,
          vendors,
          riskResult,
          reports,
          departmentName,
          fileName,
        }),
      );
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session, departmentName, fileName]);

  React.useEffect(() => {
    void load();
  }, [load]);

  React.useEffect(() => {
    const refresh = () => void load();
    window.addEventListener(DEMO_ARTIFACTS_CHANGED, refresh);
    return () => window.removeEventListener(DEMO_ARTIFACTS_CHANGED, refresh);
  }, [load]);

  if (auth.isLoading) return <AuthLoadingShell />;
  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="مركز القيادة التنفيذي"
      subtitle={org.reportingPeriod ?? undefined}
      activeItemId="dashboard"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={dashboardPageSpacingClassName}>
          <header className="space-y-2">
            <p className="text-sm font-medium text-gold-dark">
              {org.executiveTitle} — {org.name}
            </p>
            <h1 className="text-[1.75rem] font-semibold tracking-tight text-black-primary md:text-[2rem]">
              مركز القيادة التنفيذي
            </h1>
            <p className="max-w-3xl text-[15px] leading-relaxed text-muted md:text-base">
              قصة البيانات المالية — ما حدث بعد الرفع، أين الخطر، وما القرار الموصى به.
            </p>
          </header>

          {error ? (
            <ErrorState
              title="تعذّر تحميل مركز القيادة"
              description={error}
              onRetry={() => void load()}
            />
          ) : null}

          {loading ? (
            <LoadingSkeleton className="min-h-[420px] rounded-2xl" />
          ) : commandCenter ? (
            <>
              <ExecutiveHealthBanner
                score={commandCenter.healthScore}
                level={commandCenter.healthLevel}
                labelAr={commandCenter.healthLabelAr}
              />

              <ExecutiveBriefPanel
                brief={commandCenter.brief}
                briefParts={commandCenter.briefParts}
                briefFacts={commandCenter.briefFacts}
                briefSections={commandCenter.briefSections}
                boardRecommendation={commandCenter.boardRecommendation}
                narrativeStatus={commandCenter.narrativeStatus}
              />

              <ExecutiveDecisionPipeline steps={commandCenter.pipeline} />

              <ExecutiveIndicatorGrid indicators={commandCenter.indicators} />

              <ExecutiveAlertsPanel alerts={commandCenter.alerts} />

              <ExecutiveStoryTimeline steps={commandCenter.storySteps} />

              <ExecutiveWasteChart data={commandCenter.departmentChart} />
            </>
          ) : null}

          <section className={dashboardSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="التوصيات ذات الأولوية"
              description="قرارات تنفيذية جاهزة للتنفيذ"
            />
            {loading ? (
              <LoadingSkeleton className="min-h-[180px] rounded-2xl" />
            ) : recommendations.length === 0 ? (
              <EmptyState
                title="لا توجد توصيات"
                description="نفّذ كشف الهدر والمخاطر لإنشاء توصيات تنفيذية"
              />
            ) : (
              <div className="grid gap-5 lg:grid-cols-3 lg:gap-5">
                {recommendations.map((item) => {
                  const display = formatRecommendationDisplay({
                    title: item.title,
                    description: item.description,
                  });
                  return (
                    <DashboardRecommendationCard
                      key={item.id}
                      id={item.id}
                      title={display.title}
                      description={display.description}
                      badge={item.badge}
                      confidence={item.confidence}
                      href={navRouteMap.waste}
                    />
                  );
                })}
              </div>
            )}
          </section>

          <section className={dashboardSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="التحليلات الأخيرة"
              description="سجل التحليلات المكتملة"
            />
            {loading ? (
              <LoadingSkeleton className="min-h-[200px] rounded-2xl" />
            ) : analyses.length === 0 ? (
              <EmptyState
                title="لا توجد تحليلات مكتملة"
                description="ارفع البيانات ونفّذ الهدر أو المخاطر أو المحاكاة"
              />
            ) : (
              <DashboardAnalysesTable data={analyses} />
            )}
          </section>
        </div>
      </PageContainer>
    </AppLayout>
  );
}
