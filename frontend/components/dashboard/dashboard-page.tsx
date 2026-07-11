"use client";

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
import { executivePageContainerClassName, getAppNavItems } from "@/lib/app-nav";

/** Dashboard-only density experiment: ~15–20% tighter than the shared tokens */
const dashboardPageSpacingClassName = "space-y-[2.75rem] md:space-y-[3.25rem]";
const dashboardSectionSpacingClassName = "space-y-4 md:space-y-5";
import {
  dashboardKpis,
  dashboardRecommendations,
  organization,
  recentAnalyses,
  timelineEvents,
} from "@/lib/placeholder-data";

const kpiIcons = [
  TrendingDown,
  AlertTriangle,
  PiggyBank,
  BrainCircuit,
  ClipboardCheck,
];

export function DashboardPage() {
  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="لوحة التحكم"
      subtitle={organization.reportingPeriod}
      activeItemId="dashboard"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={dashboardPageSpacingClassName}>
          <DashboardHero
            title="نظرة تنفيذية"
            description={`${organization.executiveTitle} — ${organization.name}`}
            period={organization.reportingPeriod}
          />

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

          <DashboardCharts />

          <section className={dashboardSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="التوصيات ذات الأولوية"
              description="أهم التوصيات للمراجعة التنفيذية"
            />
            <div className="grid gap-5 lg:grid-cols-3 lg:gap-5">
              {dashboardRecommendations.map((item) => (
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
          </section>

          <section className={dashboardSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="آخر التحديثات"
              description="أحدث الأحداث المالية المهمة"
            />
            <div className="rounded-2xl border border-border/60 bg-surface px-4 py-4 md:px-5 md:py-4">
              <DashboardTimeline events={timelineEvents} maxVisible={5} />
            </div>
          </section>

          <section className={dashboardSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="التحليلات الأخيرة"
              description="آخر خمسة تحليلات مرتبطة بالملفات المرفوعة"
            />
            <DashboardAnalysesTable data={recentAnalyses} />
          </section>
        </div>
      </PageContainer>
    </AppLayout>
  );
}
