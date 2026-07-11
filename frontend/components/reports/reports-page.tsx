"use client";

import * as React from "react";
import { FileBarChart, FileCheck2, FileClock, Files } from "lucide-react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { ReportsCard } from "@/components/reports/reports-card";
import { ReportsExportPanel } from "@/components/reports/reports-export-panel";
import { ReportsHistoryTable } from "@/components/reports/reports-history-table";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PageHeader } from "@/components/ui/page-header";
import { executivePageContainerClassName, getAppNavItems } from "@/lib/app-nav";
import {
  organization,
  reportFilterOptions,
  reportItems,
  reportSummaryKpis,
} from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

const summaryIcons = [Files, FileCheck2, FileClock, FileBarChart];

export function ReportsPage() {
  const [typeFilter, setTypeFilter] = React.useState("الكل");
  const [departmentFilter, setDepartmentFilter] = React.useState("الكل");
  const [periodFilter, setPeriodFilter] = React.useState("الربع الحالي");
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const timer = window.setTimeout(() => setIsLoading(false), 900);
    return () => window.clearTimeout(timer);
  }, []);

  const filteredReports = React.useMemo(() => {
    return reportItems.filter((report) => {
      const typeMatch = typeFilter === "الكل" || report.type === typeFilter;
      const deptMatch =
        departmentFilter === "الكل" || report.department === departmentFilter;
      return typeMatch && deptMatch;
    });
  }, [typeFilter, departmentFilter]);

  const periodBadge = (
    <span className="inline-flex items-center rounded-full border border-gold-primary/30 bg-gold-primary/[0.07] px-3 py-1 text-xs font-medium text-gold-dark">
      {organization.reportingPeriod}
    </span>
  );

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="التقارير"
      subtitle={organization.reportingPeriod}
      activeItemId="reports"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className="space-y-[4.5rem] md:space-y-[5.5rem]">
          <PageHeader
            compact
            title="التقارير"
            description="عرض وتصفية وتصدير التقارير المالية والتحليلية للمراجعة التنفيذية."
            meta={periodBadge}
            className="!pb-3 md:!pb-4"
          />

          {isLoading ? (
            <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
              {Array.from({ length: 4 }).map((_, index) => (
                <LoadingSkeleton key={index} className="min-h-[188px] rounded-2xl" />
              ))}
            </div>
          ) : (
            <section className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4 xl:gap-7">
              {reportSummaryKpis.map((kpi, index) => {
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
          )}

          <section className="space-y-6">
            <DashboardSectionHeader
              title="تصفية التقارير"
              description="تصفية حسب النوع والقسم والفترة"
            />
            <div className="flex flex-wrap gap-6 rounded-2xl border border-border/60 bg-surface px-6 py-6 md:px-8 md:py-7">
              <FilterGroup
                label="النوع"
                options={reportFilterOptions.type}
                value={typeFilter}
                onChange={setTypeFilter}
              />
              <FilterGroup
                label="القسم"
                options={reportFilterOptions.department}
                value={departmentFilter}
                onChange={setDepartmentFilter}
              />
              <FilterGroup
                label="الفترة"
                options={reportFilterOptions.period}
                value={periodFilter}
                onChange={setPeriodFilter}
              />
            </div>
          </section>

          <section className="space-y-9 md:space-y-10">
            <DashboardSectionHeader
              title="التقارير المُنشأة"
              description="معاينة التقارير الجاهزة والمسودات"
            />
            {isLoading ? (
              <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 5 }).map((_, index) => (
                  <LoadingSkeleton key={index} className="min-h-[320px] rounded-2xl" />
                ))}
              </div>
            ) : filteredReports.length === 0 ? (
              <EmptyState
                title="لا توجد تقارير"
                description="سيتم إنشاء التقارير بعد إتمام التحليلات"
              />
            ) : (
              <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3 xl:gap-7">
                {filteredReports.map((report) => (
                  <ReportsCard key={report.id} report={report} />
                ))}
              </div>
            )}
          </section>

          <section className="space-y-9 md:space-y-10">
            <DashboardSectionHeader
              title="سجل التقارير"
              description="سجل كامل للتقارير المُنشأة"
            />
            {isLoading ? (
              <LoadingSkeleton className="min-h-[320px] rounded-2xl" />
            ) : (
              <ReportsHistoryTable reports={filteredReports} />
            )}
          </section>

          <section className="space-y-9 md:space-y-10">
            <ReportsExportPanel />
          </section>
        </div>
      </PageContainer>
    </AppLayout>
  );
}

interface FilterGroupProps {
  label: string;
  options: readonly string[];
  value: string;
  onChange: (value: string) => void;
}

function FilterGroup({ label, options, value, onChange }: FilterGroupProps) {
  return (
    <div className="space-y-3">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">
        {label}
      </p>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onChange(option)}
            className={cn(
              "rounded-full border px-4 py-2 text-sm font-medium transition-colors",
              value === option
                ? "border-gold-primary bg-gold-primary text-white"
                : "border-border/70 bg-surface text-gray-medium hover:bg-bg-light",
            )}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
