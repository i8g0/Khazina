"use client";

import {
  AlertTriangle,
  BarChart3,
  BrainCircuit,
  ClipboardCheck,
  Database,
  FileBarChart,
  LayoutDashboard,
  LineChart,
  PiggyBank,
  ScanSearch,
  ShieldAlert,
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
import {
  dashboardKpis,
  dashboardNavItems,
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

const navIcons: Record<string, React.ReactNode> = {
  dashboard: <LayoutDashboard className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  waste: <ScanSearch className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  risk: <ShieldAlert className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  simulation: <LineChart className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  reports: <FileBarChart className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  data: <Database className="h-[18px] w-[18px]" strokeWidth={1.75} />,
};

export function DashboardPage() {
  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="لوحة التحكم"
      subtitle={organization.reportingPeriod}
      activeItemId="dashboard"
      sidebarVariant="executive"
      navItems={dashboardNavItems.map((item) => ({
        id: item.id,
        label: item.label,
        icon: navIcons[item.id] ?? <BarChart3 className="h-[18px] w-[18px]" strokeWidth={1.75} />,
      }))}
    >
      <PageContainer className="max-w-[1720px] px-5 py-12 md:px-8 md:py-14 lg:px-10">
        <div className="space-y-16 md:space-y-20">
          <DashboardHero
            title="نظرة تنفيذية"
            description={`${organization.executiveTitle} — ${organization.name}`}
            period={organization.reportingPeriod}
          />

          <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-5 xl:gap-6">
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
                  icon={<Icon className="h-[17px] w-[17px]" strokeWidth={1.75} />}
                />
              );
            })}
          </section>

          <DashboardCharts />

          <section className="space-y-8">
            <DashboardSectionHeader
              title="التوصيات ذات الأولوية"
              description="أهم التوصيات للمراجعة التنفيذية"
            />
            <div className="grid gap-6 lg:grid-cols-3 lg:gap-7">
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

          <section className="space-y-8">
            <DashboardSectionHeader
              title="آخر التحديثات"
              description="أحدث الأحداث المالية المهمة"
            />
            <div className="rounded-2xl border border-border/60 bg-surface px-8 py-8 md:px-10 md:py-10">
              <DashboardTimeline events={timelineEvents} maxVisible={5} />
            </div>
          </section>

          <section className="space-y-8">
            <DashboardSectionHeader
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
