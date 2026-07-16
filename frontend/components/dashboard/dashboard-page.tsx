"use client";

import * as React from "react";
import {
  AlertTriangle,
  BrainCircuit,
  ClipboardCheck,
  PiggyBank,
  TrendingDown,
} from "lucide-react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardAnalysesTable } from "@/components/dashboard/dashboard-analyses-table";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardCharts } from "@/components/dashboard/dashboard-charts";
import { DashboardHero } from "@/components/dashboard/dashboard-hero";
import { DashboardGuidanceHero } from "@/components/workflow/dashboard-guidance-hero";
import { SystemStatusBanner } from "@/components/workflow/system-status-banner";
import { WorkflowIndicator } from "@/components/workflow/workflow-indicator";
import { AuthLoadingShell } from "@/components/workflow/auth-loading-shell";
import { EXECUTIVE_MESSAGES } from "@/lib/workflow/messages";
import { DashboardRecommendationCard } from "@/components/dashboard/dashboard-recommendation-card";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { DashboardTimeline } from "@/components/dashboard/dashboard-timeline";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { executivePageContainerClassName, getAppNavGroups } from "@/lib/app-nav";
import {
  type RecentAnalysis,
  type TimelineEvent,
} from "@/lib/placeholder-data";
import {
  useRequireAuth,
  formatApiError,
} from "@/lib/auth/auth-context";
import { useOrganizationDisplay, useOrgLookups } from "@/lib/org-lookups";
import {
  listRecentAnalyses,
  listRecommendations,
  listRisks,
  listTimeline,
} from "@/lib/api/khazina-api";
import {
  formatDate,
  formatRecommendationDisplay,
  mapAnalysisType,
  mapRecommendationPriority,
  mapRunStatus,
  mapTimelineType,
} from "@/lib/format";

const dashboardPageSpacingClassName = "space-y-[2.75rem] md:space-y-[3.25rem]";
const dashboardSectionSpacingClassName = "space-y-4 md:space-y-5";

const kpiIcons = [
  TrendingDown,
  AlertTriangle,
  PiggyBank,
  BrainCircuit,
  ClipboardCheck,
];

const dashboardKpiLabels = [
  "إجمالي الهدر المالي المكتشف",
  "عدد المخاطر الحرجة",
  "التوفير المتوقع",
  "آخر توصية من الذكاء الاصطناعي",
  "حالة آخر تحليل",
];

const dashboardKpiEmptyMessage = EXECUTIVE_MESSAGES.dashboardKpiEmpty;

export function DashboardPage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const { fileName } = useOrgLookups();
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [timeline, setTimeline] = React.useState<TimelineEvent[]>([]);
  const [analyses, setAnalyses] = React.useState<RecentAnalysis[]>([]);
  const [recommendations, setRecommendations] = React.useState<
    { id: string; title: string; description: string; badge: string; confidence: string }[]
  >([]);
  const [kpiValues, setKpiValues] = React.useState<(string | null)[]>([
    null,
    null,
    null,
    null,
    null,
  ]);

  const load = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    try {
      const [events, runs, recs, risks] = await Promise.all([
        listTimeline(auth.session.organizationId, auth.session.token),
        listRecentAnalyses(auth.session.organizationId, auth.session.token),
        listRecommendations(auth.session.organizationId, auth.session.token),
        listRisks(auth.session.organizationId, auth.session.token, { limit: 50 }),
      ]);
      setTimeline(
        events.slice(0, 5).map((event) => ({
          id: event.id,
          date: event.event_date,
          title: event.title,
          type: mapTimelineType(event.event_type),
        })),
      );
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

      const riskHigh = risks.filter(
        (r) => r.priority === "high" && r.status !== "closed",
      ).length;
      const latestRec = recs[0];
      const latestRun = runs[0];

      setKpiValues([
        null,
        riskHigh > 0 ? String(riskHigh) : null,
        null,
        latestRec ? latestRec.title.slice(0, 40) : null,
        latestRun ? mapRunStatus(latestRun.status) : null,
      ]);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session, fileName]);

  React.useEffect(() => {
    void load();
  }, [load]);

  if (auth.isLoading) return <AuthLoadingShell />;
  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="لوحة التحكم"
      subtitle={org.reportingPeriod ?? undefined}
      activeItemId="dashboard"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={dashboardPageSpacingClassName}>
          <DashboardGuidanceHero
            orgName={org.name}
            executiveTitle={org.executiveTitle}
            period={org.reportingPeriod}
          />

          <SystemStatusBanner />

          <WorkflowIndicator />

          <DashboardHero
            title="نظرة تنفيذية"
            description={`${org.executiveTitle} — ${org.name}`}
            period={org.reportingPeriod}
          />

          {error ? (
            <ErrorState
              title="تعذّر تحميل لوحة التحكم"
              description={error}
              onRetry={() => void load()}
            />
          ) : null}

          <section className="space-y-3">
            <DashboardSectionHeader
              dense
              title="مؤشرات الأداء"
              description={EXECUTIVE_MESSAGES.dashboardKpiSection}
            />
            <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-5 xl:gap-5">
              {dashboardKpiLabels.map((label, index) => {
                const Icon = kpiIcons[index];
                const liveValue = kpiValues[index];
                return (
                  <DashboardStatCard
                    key={label}
                    label={label}
                    value={
                      liveValue ? (
                        <span className="text-2xl font-semibold tabular-nums text-black-primary">
                          {liveValue}
                        </span>
                      ) : (
                        <span className="text-sm font-normal leading-relaxed text-muted">
                          {dashboardKpiEmptyMessage}
                        </span>
                      )
                    }
                    hint={liveValue ? undefined : EXECUTIVE_MESSAGES.dashboardKpiHint}
                    emphasis
                    dense
                    icon={<Icon className="h-[17px] w-[17px]" strokeWidth={1.75} />}
                  />
                );
              })}
            </section>
          </section>

          <section className="space-y-3">
            <DashboardSectionHeader dense title="الرسوم البيانية" />
            <DashboardCharts />
          </section>

          <section className={dashboardSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="التوصيات ذات الأولوية"
              description="من سجل التوصيات الحي"
            />
            {loading ? (
              <LoadingSkeleton className="min-h-[180px] rounded-2xl" />
            ) : recommendations.length === 0 ? (
              <EmptyState
                title="لا توجد توصيات"
                description="شغّل تحليل الهدر والذكاء الاصطناعي لعرض التوصيات"
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
                    />
                  );
                })}
              </div>
            )}
          </section>

          <section className={dashboardSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="آخر التحديثات"
              description="أحدث الأحداث من الجدول الزمني"
            />
            {loading ? (
              <LoadingSkeleton className="min-h-[120px] rounded-2xl" />
            ) : timeline.length === 0 ? (
              <EmptyState
                title="لا أحداث بعد"
                description="ستظهر أحداث المنصة هنا بعد إكمال التحليلات"
              />
            ) : (
              <div className="rounded-2xl border border-border/60 bg-surface px-4 py-4 md:px-5 md:py-4">
                <DashboardTimeline events={timeline} maxVisible={5} />
              </div>
            )}
          </section>

          <section className={dashboardSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="التحليلات الأخيرة"
              description="آخر التحليلات المكتملة"
            />
            {loading ? (
              <LoadingSkeleton className="min-h-[200px] rounded-2xl" />
            ) : analyses.length === 0 ? (
              <EmptyState
                title="لا توجد تحليلات مكتملة"
                description="نفّذ كشف الهدر أو المحاكاة لملء هذه القائمة"
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
