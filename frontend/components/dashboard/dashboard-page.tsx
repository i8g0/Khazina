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
import { DashboardRecommendationCard } from "@/components/dashboard/dashboard-recommendation-card";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { DashboardTimeline } from "@/components/dashboard/dashboard-timeline";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Badge } from "@/components/ui/badge";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { executivePageContainerClassName, getAppNavItems } from "@/lib/app-nav";
import {
  dashboardKpis,
  organization,
  type RecentAnalysis,
  type TimelineEvent,
} from "@/lib/placeholder-data";
import { useRequireAuth, formatApiError } from "@/lib/auth/auth-context";
import {
  listRecentAnalyses,
  listRecommendations,
  listTimeline,
} from "@/lib/api/khazina-api";
import {
  formatDate,
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

export function DashboardPage() {
  const auth = useRequireAuth();
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [timeline, setTimeline] = React.useState<TimelineEvent[]>([]);
  const [analyses, setAnalyses] = React.useState<RecentAnalysis[]>([]);
  const [recommendations, setRecommendations] = React.useState<
    { id: string; title: string; description: string; badge: string; confidence: string }[]
  >([]);

  React.useEffect(() => {
    if (!auth.session) return;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [events, runs, recs] = await Promise.all([
          listTimeline(auth.session!.organizationId, auth.session!.token),
          listRecentAnalyses(auth.session!.organizationId, auth.session!.token),
          listRecommendations(auth.session!.organizationId, auth.session!.token),
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
            sourceFile: "Procurement_Q2.xlsx",
            date: run.completed_at ? formatDate(run.completed_at) : "—",
            status: mapRunStatus(run.status),
          })),
        );
        setRecommendations(
          recs.slice(0, 3).map((rec) => ({
            id: rec.id,
            title: rec.title,
            description: rec.description,
            badge: mapRecommendationPriority(rec.priority),
            confidence: rec.confidence_label ?? "—",
          })),
        );
      } catch (err) {
        setError(formatApiError(err));
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [auth.session]);

  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="لوحة التحكم"
      subtitle={organization.reportingPeriod}
      activeItemId="dashboard"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={dashboardPageSpacingClassName}>
          <DashboardHero
            title="نظرة تنفيذية"
            description={`${organization.executiveTitle} — ${organization.name}`}
            period={organization.reportingPeriod}
          />

          {error ? (
            <ErrorState title="خطأ" description={error} onRetry={() => setError(null)} />
          ) : null}

          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <DashboardSectionHeader
                dense
                title="مؤشرات الأداء"
                description="بيانات مرجعية للعرض — التكامل الكامل في مرحلة لاحقة"
              />
              <Badge variant="outline">عرض توضيحي</Badge>
            </div>
            <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-5 xl:gap-5">
              {dashboardKpis.map((kpi, index) => {
                const Icon = kpiIcons[index];
                return (
                  <DashboardStatCard
                    key={kpi.label}
                    label={kpi.label}
                    value={kpi.value}
                    hint={kpi.hint}
                    departmentBadge={kpi.departmentBadge}
                    trend={kpi.trend}
                    emphasis
                    dense
                    icon={<Icon className="h-[17px] w-[17px]" strokeWidth={1.75} />}
                  />
                );
              })}
            </section>
          </section>

          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <DashboardSectionHeader dense title="الرسوم البيانية" />
              <Badge variant="outline">عرض توضيحي</Badge>
            </div>
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
              <p className="text-sm text-muted">لا توجد توصيات بعد — شغّل تحليل الهدر والذكاء الاصطناعي</p>
            ) : (
              <div className="grid gap-5 lg:grid-cols-3 lg:gap-5">
                {recommendations.map((item) => (
                  <DashboardRecommendationCard
                    key={item.id}
                    id={item.id}
                    title={item.title}
                    description={item.description}
                    badge={item.badge}
                    confidence={item.confidence}
                  />
                ))}
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
            ) : (
              <DashboardAnalysesTable data={analyses} />
            )}
          </section>
        </div>
      </PageContainer>
    </AppLayout>
  );
}
