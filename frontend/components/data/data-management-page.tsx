"use client";

import * as React from "react";
import { Database, FileCheck2, FileStack, ShieldCheck } from "lucide-react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { DataSummaryCards } from "@/components/data/data-summary-cards";
import { ImportHistoryTable } from "@/components/data/import-history-table";
import { UploadDataPanel } from "@/components/data/upload-data-panel";
import { UploadedFilesTable } from "@/components/data/uploaded-files-table";
import { Alert } from "@/components/ui/alert";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { PageHeader } from "@/components/ui/page-header";
import { executivePageContainerClassName, getAppNavItems } from "@/lib/app-nav";
import {
  dataSummaryKpis,
  dataValidationSummary,
  importHistory,
  organization,
  uploadedFiles,
} from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

type DataViewState = "idle" | "loading" | "ready";

const summaryIcons = [FileStack, Database, FileCheck2, ShieldCheck];
const LOADING_MS = 1400;

export function DataManagementPage() {
  const [viewState, setViewState] = React.useState<DataViewState>("idle");
  const [uploadedFileName, setUploadedFileName] = React.useState<string | null>(null);

  const handleUpload = React.useCallback((fileName: string) => {
    setUploadedFileName(fileName);
    setViewState("loading");
    window.setTimeout(() => {
      setViewState("ready");
    }, LOADING_MS);
  }, []);

  const periodBadge = (
    <span className="inline-flex items-center rounded-full border border-gold-primary/30 bg-gold-primary/[0.07] px-3 py-1 text-xs font-medium text-gold-dark">
      {organization.reportingPeriod}
    </span>
  );

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="إدارة البيانات"
      subtitle={organization.reportingPeriod}
      activeItemId="data"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div
          className={cn(
            viewState === "ready"
              ? "space-y-[4.5rem] md:space-y-[5.5rem]"
              : "space-y-10 md:space-y-12",
          )}
        >
          <PageHeader
            compact
            title="إدارة البيانات"
            description="رفع الملفات المالية ومتابعة سجل الاستيراد وجودة البيانات."
            meta={periodBadge}
            className="!pb-3 md:!pb-4"
          />

          <section className="relative space-y-6">
            <DashboardSectionHeader
              title="رفع مجموعة البيانات"
              description="ارفع ملفات Excel أو CSV لتحديث قاعدة البيانات المالية"
            />
            <UploadDataPanel
              disabled={viewState === "loading"}
              onUpload={handleUpload}
            />
            {viewState === "loading" ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 rounded-2xl bg-surface/85 backdrop-blur-sm">
                <LoadingSpinner size="lg" label="جاري رفع الملف..." />
                <p className="text-sm font-medium text-muted">جاري معالجة الملف...</p>
              </div>
            ) : null}
          </section>

          {viewState === "idle" ? (
            <EmptyState
              title="لا توجد ملفات"
              description="ارفع ملفات Excel أو CSV للبدء"
              actionLabel="اختيار ملف"
              onAction={() => handleUpload("Dataset.xlsx")}
            />
          ) : null}

          {viewState === "loading" ? (
            <div className="space-y-8">
              <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
                {Array.from({ length: 4 }).map((_, index) => (
                  <LoadingSkeleton key={index} className="min-h-[188px] rounded-2xl" />
                ))}
              </div>
              <LoadingSkeleton className="min-h-[320px] rounded-2xl" />
              <LoadingSkeleton className="min-h-[280px] rounded-2xl" />
            </div>
          ) : null}

          {viewState === "ready" ? (
            <>
              {uploadedFileName ? (
                <Alert variant="success" title="تم رفع الملف بنجاح">
                  تم استلام {uploadedFileName} — البيانات المعروضة من المصادر الحالية.
                </Alert>
              ) : null}

              <section className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4 xl:gap-7">
                {dataSummaryKpis.map((kpi, index) => {
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
                  title="الملفات المرفوعة"
                  description="سجل الملفات المالية المتاحة للتحليل"
                />
                <UploadedFilesTable files={uploadedFiles} />
              </section>

              <section className="space-y-9 md:space-y-10">
                <DashboardSectionHeader
                  title="سجل الاستيراد"
                  description="تاريخ عمليات استيراد البيانات"
                />
                <ImportHistoryTable items={importHistory} />
              </section>

              <section className="space-y-9 md:space-y-10">
                <DashboardSectionHeader
                  title="ملخص جودة البيانات"
                  description="نتائج فحوصات التحقق من سلامة البيانات"
                />
                <DataSummaryCards validationItems={dataValidationSummary} />
              </section>
            </>
          ) : null}
        </div>
      </PageContainer>
    </AppLayout>
  );
}
