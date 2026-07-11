"use client";

import * as React from "react";
import { Database, FileCheck2, FileStack, HardDrive } from "lucide-react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { DataSummaryCards } from "@/components/data/data-summary-cards";
import { ImportHistoryTable } from "@/components/data/import-history-table";
import { UploadDataPanel } from "@/components/data/upload-data-panel";
import { UploadedFilesTable } from "@/components/data/uploaded-files-table";
import { Alert } from "@/components/ui/alert";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PageHero } from "@/components/ui/page-hero";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavItems,
} from "@/lib/app-nav";
import {
  dataSummaryKpis,
  dataValidationSummary,
  importHistory,
  organization,
  uploadedFiles,
} from "@/lib/placeholder-data";

type DataViewState = "ready" | "loading";

const summaryIcons = [FileStack, Database, HardDrive, FileCheck2];
const LOADING_MS = 1200;

export function DataManagementPage() {
  const [viewState, setViewState] = React.useState<DataViewState>("ready");
  const [uploadedFileName, setUploadedFileName] = React.useState<string | null>(null);

  const handleUpload = React.useCallback((fileName: string) => {
    setUploadedFileName(fileName);
    setViewState("loading");
    window.setTimeout(() => {
      setViewState("ready");
    }, LOADING_MS);
  }, []);

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="مستودع البيانات"
      subtitle={organization.reportingPeriod}
      activeItemId="data"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="مستودع البيانات المالية"
            description="إدارة مجموعات البيانات المؤسسية — حالة الملفات، سجل الاستيراد، وجودة البيانات."
            period={organization.reportingPeriod}
          />

          {uploadedFileName && viewState === "ready" ? (
            <Alert variant="success" title="تم تحديث المستودع">
              تم استلام {uploadedFileName} — البيانات المعروضة من المصادر الحالية.
            </Alert>
          ) : null}

          {viewState === "loading" ? (
            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
              {Array.from({ length: 4 }).map((_, index) => (
                <LoadingSkeleton key={index} className="min-h-[176px] rounded-2xl" />
              ))}
            </div>
          ) : (
            <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4 xl:gap-5">
              {dataSummaryKpis.map((kpi, index) => {
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
          )}

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="الملفات المرفوعة"
              description="مجموعات البيانات المالية المتاحة للتحليل والتقارير"
            />
            {viewState === "loading" ? (
              <LoadingSkeleton className="min-h-[280px] rounded-2xl" />
            ) : (
              <UploadedFilesTable files={uploadedFiles} />
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="سجل الاستيراد"
              description="تاريخ عمليات استيراد البيانات وحالة المعالجة"
            />
            {viewState === "loading" ? (
              <LoadingSkeleton className="min-h-[240px] rounded-2xl" />
            ) : (
              <ImportHistoryTable items={importHistory} />
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="صحة البيانات والتحقق"
              description="نتائج فحوصات جودة البيانات وسجل التحقق"
            />
            {viewState === "loading" ? (
              <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
                {Array.from({ length: 4 }).map((_, index) => (
                  <LoadingSkeleton key={index} className="min-h-[176px] rounded-2xl" />
                ))}
              </div>
            ) : (
              <DataSummaryCards validationItems={dataValidationSummary} />
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="إضافة ملف للمستودع"
              description="رفع ملف جديد — عملية ثانوية لتحديث مجموعة البيانات"
            />
            <UploadDataPanel
              compact
              disabled={viewState === "loading"}
              onUpload={handleUpload}
            />
          </section>
        </div>
      </PageContainer>
    </AppLayout>
  );
}
