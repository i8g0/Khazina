"use client";

import * as React from "react";
import {
  BarChart3,
  FileSpreadsheet,
  PiggyBank,
  RefreshCw,
  TrendingDown,
} from "lucide-react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { WasteAiFindingCard } from "@/components/waste/waste-ai-finding-card";
import { WasteBreakdownTable } from "@/components/waste/waste-breakdown-table";
import { WasteCharts } from "@/components/waste/waste-charts";
import { WasteDepartmentBreakdown } from "@/components/waste/waste-department-breakdown";
import { WasteIdleContent } from "@/components/waste/waste-idle-content";
import { WasteSavingsCard } from "@/components/waste/waste-savings-card";
import { Button } from "@/components/ui/button";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { PageHero } from "@/components/ui/page-hero";
import { UploadArea } from "@/components/ui/upload-area";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavItems,
} from "@/lib/app-nav";
import {
  organization,
  wasteAnalysisResults,
  wasteDepartmentFilterOptions,
  wasteRecommendations,
  wasteSummaryKpis,
  wasteVendorDetails,
} from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

type WasteViewState = "idle" | "loading" | "ready";

const summaryIcons = [TrendingDown, BarChart3, FileSpreadsheet, PiggyBank];

const LOADING_MS = 1400;

export function WastePage() {
  const uploadInputRef = React.useRef<HTMLInputElement>(null);
  const [viewState, setViewState] = React.useState<WasteViewState>("idle");
  const [departmentFilter, setDepartmentFilter] = React.useState<string>("الكل");
  const [uploadedFileName, setUploadedFileName] = React.useState<string | null>(
    null,
  );

  const runAnalysis = React.useCallback((fileName?: string) => {
    setViewState("loading");
    if (fileName) {
      setUploadedFileName(fileName);
    }
    window.setTimeout(() => {
      setViewState("ready");
    }, LOADING_MS);
  }, []);

  const openUploadPicker = React.useCallback(() => {
    uploadInputRef.current?.click();
  }, []);

  const filteredAnalysisRows = React.useMemo(() => {
    if (departmentFilter === "الكل") {
      return wasteAnalysisResults;
    }
    return wasteAnalysisResults.filter(
      (row) => row.department === departmentFilter,
    );
  }, [departmentFilter]);

  const filteredVendorRows = React.useMemo(() => {
    if (departmentFilter === "الكل") {
      return wasteVendorDetails;
    }
    return wasteVendorDetails;
  }, [departmentFilter]);

  const aiFindings = wasteRecommendations.filter((item) => item.badge === "عالية").slice(0, 2);

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="كشف الهدر"
      subtitle={organization.reportingPeriod}
      activeItemId="waste"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div
          className={cn(
            viewState === "ready"
              ? executivePageSpacingClassName
              : "space-y-4 md:space-y-5",
          )}
        >
          <PageHero
            title="كشف الهدر المالي"
            description="رفع ملفات مالية وتحليل أنماط الهدر وفرص التوفير المؤسسية"
            period={organization.reportingPeriod}
            actions={
              viewState === "ready" ? (
                <Button
                  variant="secondary"
                  onClick={() => runAnalysis(uploadedFileName ?? undefined)}
                >
                  <RefreshCw className="h-4 w-4" strokeWidth={1.75} />
                  إعادة التحليل
                </Button>
              ) : null
            }
          />

          <section className="relative space-y-0">
            <input
              ref={uploadInputRef}
              type="file"
              className="hidden"
              accept=".xlsx,.xls,.csv"
              disabled={viewState === "loading"}
              onChange={(event) => {
                const file = event.target.files?.[0];
                runAnalysis(file?.name ?? "Procurement_Q2.xlsx");
              }}
            />
            <UploadArea
              variant="prominent"
              title="اسحب ملف Excel أو CSV هنا"
              description="يدعم .xlsx و .xls و .csv — حتى 10 ميغابايت · ابدأ من هنا"
              accept=".xlsx,.xls,.csv"
              actionLabel="اختيار ملف للتحليل"
              disabled={viewState === "loading"}
              onFilesSelected={(files) => {
                runAnalysis(files[0]?.name ?? "Procurement_Q2.xlsx");
              }}
            />
            {viewState === "loading" ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 rounded-2xl bg-surface/85 backdrop-blur-sm">
                <LoadingSpinner size="lg" label="جاري تحليل الملف..." />
                <p className="text-sm font-medium text-muted">جاري تحليل الملف...</p>
              </div>
            ) : null}
          </section>

          {viewState === "idle" ? (
            <WasteIdleContent onUploadClick={openUploadPicker} />
          ) : null}

          {viewState === "loading" ? (
            <div className="space-y-8">
              <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4 xl:gap-5">
                {Array.from({ length: 4 }).map((_, index) => (
                  <LoadingSkeleton key={index} className="min-h-[168px] rounded-2xl" />
                ))}
              </div>
              <div className="grid gap-5 xl:grid-cols-2">
                <LoadingSkeleton className="min-h-[460px] rounded-2xl" />
                <LoadingSkeleton className="min-h-[460px] rounded-2xl" />
              </div>
              <LoadingSkeleton className="min-h-[320px] rounded-2xl" />
            </div>
          ) : null}

          {viewState === "ready" ? (
            <>
              <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4 xl:gap-5">
                {wasteSummaryKpis.map((kpi, index) => {
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

              <WasteCharts />

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader
                  dense
                  title="توزيع الهدر حسب الإدارات"
                  description="مقارنة مساهمة كل إدارة في إجمالي الهدر المكتشف"
                />
                <WasteDepartmentBreakdown />
              </section>

              <section className={executiveSectionSpacingClassName}>
                <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                  <DashboardSectionHeader
                    dense
                    title="تفاصيل الهدر المالي"
                    description="تحليل الفئات والموردين مع إمكانية التصفية حسب الإدارة"
                  />
                  <div className="flex flex-wrap gap-2">
                    {wasteDepartmentFilterOptions.map((option) => (
                      <button
                        key={option}
                        type="button"
                        onClick={() => setDepartmentFilter(option)}
                        className={cn(
                          "rounded-full border px-4 py-2 text-sm font-medium transition-colors",
                          departmentFilter === option
                            ? "border-gold-primary bg-gold-primary text-white"
                            : "border-border/70 bg-surface text-gray-medium hover:bg-bg-light",
                        )}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                </div>
                <WasteBreakdownTable
                  analysisRows={filteredAnalysisRows}
                  vendorRows={filteredVendorRows}
                />
              </section>

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader
                  dense
                  title="نتائج الذكاء الاصطناعي"
                  description="أهم الملاحظات المكتشفة آلياً من تحليل البيانات المرفوعة"
                />
                <div className="grid gap-5 lg:grid-cols-2 lg:gap-5">
                  {aiFindings.map((item) => (
                    <WasteAiFindingCard key={item.id} item={item} />
                  ))}
                </div>
              </section>

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader
                  dense
                  title="فرص التوفير"
                  description="توصيات قابلة للتنفيذ مع تقدير التوفير المحتمل"
                />
                <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4 xl:gap-5">
                  {wasteRecommendations.map((item) => (
                    <WasteSavingsCard key={item.id} item={item} />
                  ))}
                </div>
              </section>
            </>
          ) : null}
        </div>
      </PageContainer>
    </AppLayout>
  );
}
