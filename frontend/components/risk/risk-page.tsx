"use client";

import { AlertTriangle, CheckCircle2, ShieldAlert, ShieldCheck } from "lucide-react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { RiskActiveTable } from "@/components/risk/risk-active-table";
import { RiskCharts } from "@/components/risk/risk-charts";
import { RiskMitigationPlans } from "@/components/risk/risk-mitigation-plans";
import { RiskPriorityMatrix } from "@/components/risk/risk-priority-matrix";
import { RiskRecommendationCard } from "@/components/risk/risk-recommendation-card";
import { PageHeader } from "@/components/ui/page-header";
import { executivePageContainerClassName, getAppNavItems } from "@/lib/app-nav";
import { organization, riskRecommendations, riskSummaryKpis } from "@/lib/placeholder-data";

const summaryIcons = [ShieldAlert, AlertTriangle, ShieldCheck, CheckCircle2];

export function RiskPage() {
  const periodBadge = (
    <span className="inline-flex items-center rounded-full border border-gold-primary/30 bg-gold-primary/[0.07] px-3 py-1 text-xs font-medium text-gold-dark">
      {organization.reportingPeriod}
    </span>
  );

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="إدارة المخاطر"
      subtitle={organization.reportingPeriod}
      activeItemId="risk"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className="space-y-[4.5rem] md:space-y-[5.5rem]">
          <PageHeader
            compact
            title="إدارة المخاطر"
            description="متابعة وتحليل المخاطر التشغيلية والمالية للمؤسسة."
            meta={periodBadge}
            className="!pb-3 md:!pb-4"
          />

          <section className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4 xl:gap-7">
            {riskSummaryKpis.map((kpi, index) => {
              const Icon = summaryIcons[index];
              return (
                <DashboardStatCard
                  key={kpi.label}
                  label={kpi.label}
                  value={kpi.value}
                  hint={kpi.hint}
                  emphasis
                  icon={<Icon className="h-[17px] w-[17px]" strokeWidth={1.75} />}
                />
              );
            })}
          </section>

          <section className="space-y-9 md:space-y-10">
            <DashboardSectionHeader
              title="توزيع المخاطر"
              description="تحليل المخاطر النشطة حسب القسم ومستوى الخطورة"
            />
            <RiskCharts />
          </section>

          <section className="space-y-9 md:space-y-10">
            <DashboardSectionHeader
              title="مصفوفة الأولوية"
              description="تصنيف المخاطر حسب الاحتمالية والتأثير"
            />
            <RiskPriorityMatrix />
          </section>

          <section className="space-y-9 md:space-y-10">
            <DashboardSectionHeader
              title="المخاطر النشطة"
              description="سجل المخاطر الحالية مع الأولوية والمسؤولية"
            />
            <RiskActiveTable />
          </section>

          <section className="space-y-9 md:space-y-10">
            <DashboardSectionHeader
              title="توصيات الذكاء الاصطناعي"
              description="إجراءات مقترحة لتخفيف المخاطر ذات الأولوية"
            />
            <div className="grid gap-7 lg:grid-cols-3 lg:gap-8">
              {riskRecommendations.map((item) => (
                <RiskRecommendationCard key={item.id} item={item} />
              ))}
            </div>
          </section>

          <section className="space-y-9 md:space-y-10">
            <DashboardSectionHeader
              title="خطط التخفيف"
              description="خطط معالجة المخاطر وجداول التنفيذ"
            />
            <RiskMitigationPlans />
          </section>
        </div>
      </PageContainer>
    </AppLayout>
  );
}
