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
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Badge } from "@/components/ui/badge";
import { PageHero } from "@/components/ui/page-hero";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavItems,
} from "@/lib/app-nav";
import { organization, riskRecommendations, riskSummaryKpis } from "@/lib/placeholder-data";
import { useRequireAuth } from "@/lib/auth/auth-context";

const summaryIcons = [ShieldAlert, AlertTriangle, ShieldCheck, CheckCircle2];

export function RiskPage() {
  const auth = useRequireAuth();
  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="إدارة المخاطر"
      subtitle={organization.reportingPeriod}
      activeItemId="risk"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="إدارة المخاطر"
            description="متابعة وتحليل المخاطر التشغيلية والمالية للمؤسسة."
            period={organization.reportingPeriod}
          />

          <div className="flex items-center gap-2">
            <Badge variant="outline">عرض توضيحي — لا يوجد محرك مخاطر في المرحلة 6</Badge>
          </div>

          <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4 xl:gap-5">
            {riskSummaryKpis.map((kpi, index) => {
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
            <DashboardSectionHeader
              dense
              title="توزيع المخاطر"
              description="تحليل المخاطر النشطة حسب القسم ومستوى الخطورة"
            />
            <RiskCharts />
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="مصفوفة الأولوية"
              description="تصنيف المخاطر حسب الاحتمالية والتأثير"
            />
            <RiskPriorityMatrix />
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="المخاطر النشطة"
              description="سجل المخاطر الحالية مع الأولوية والمسؤولية"
            />
            <RiskActiveTable />
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="توصيات الذكاء الاصطناعي"
              description="إجراءات مقترحة لتخفيف المخاطر ذات الأولوية"
            />
            <div className="grid gap-5 lg:grid-cols-3 lg:gap-5">
              {riskRecommendations.map((item) => (
                <RiskRecommendationCard key={item.id} item={item} />
              ))}
            </div>
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
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
