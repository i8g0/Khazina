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
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Alert } from "@/components/ui/alert";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PageHero } from "@/components/ui/page-hero";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavItems,
} from "@/lib/app-nav";
import { organization, dataValidationSummary } from "@/lib/placeholder-data";
import type { UploadedFileItem } from "@/lib/placeholder-data";
import { useRequireAuth, formatApiError } from "@/lib/auth/auth-context";
import { listFinancialFiles, uploadFinancialFile } from "@/lib/api/khazina-api";
import { writeDemoArtifacts } from "@/lib/demo/state";
import { formatDate, mapProcessingStatus } from "@/lib/format";

const summaryIcons = [FileStack, Database, HardDrive, FileCheck2];

export function DataManagementPage() {
  const auth = useRequireAuth();
  const [loading, setLoading] = React.useState(true);
  const [uploading, setUploading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [files, setFiles] = React.useState<UploadedFileItem[]>([]);
  const [uploadMessage, setUploadMessage] = React.useState<string | null>(null);

  const loadFiles = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    try {
      const rows = await listFinancialFiles(
        auth.session.organizationId,
        auth.session.token,
      );
      setFiles(
        rows.map((row) => ({
          id: row.id,
          fileName: row.file_name,
          department: "—",
          uploadDate: formatDate(row.uploaded_at),
          size: row.size_display ?? "—",
          status: mapProcessingStatus(row.processing_status),
        })),
      );
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session]);

  React.useEffect(() => {
    if (auth.session) {
      void loadFiles();
    }
  }, [auth.session, loadFiles]);

  const handleFileUpload = async (file: File) => {
    if (!auth.session) return;
    setUploading(true);
    setUploadMessage(null);
    setError(null);
    try {
      const outcome = await uploadFinancialFile(
        auth.session.organizationId,
        auth.session.token,
        file,
      );
      if (outcome.financial_snapshot) {
        writeDemoArtifacts({
          fileId: outcome.financial_file.id,
          snapshotId: outcome.financial_snapshot.id,
          snapshotVersion: outcome.financial_snapshot.snapshot_version,
        });
      }
      setUploadMessage(`تم رفع ${file.name} بنجاح`);
      await loadFiles();
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setUploading(false);
    }
  };

  const kpis = [
    { label: "الملفات المرفوعة", value: String(files.length), hint: "مستودع البيانات" },
    { label: "جاهزة للتحليل", value: String(files.filter((f) => f.status.includes("جاهز") || f.status.includes("مكتمل")).length), hint: "حالة المعالجة" },
    { label: "آخر رفع", value: files[0]?.uploadDate ?? "—", hint: files[0]?.fileName ?? "لا يوجد" },
    { label: "جودة البيانات", value: "جيدة", hint: "تقييم أولي" },
  ];

  if (!auth.session) {
    return null;
  }

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="مستودع البيانات"
      subtitle={organization.reportingPeriod}
      activeItemId="data"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="مستودع البيانات المالية"
            description="إدارة مجموعات البيانات المؤسسية — حالة الملفات، سجل الاستيراد، وجودة البيانات."
            period={organization.reportingPeriod}
          />

          {uploadMessage ? (
            <Alert variant="success" title="تم تحديث المستودع">
              {uploadMessage}
            </Alert>
          ) : null}

          {error ? <ErrorState title="تعذّر تحميل البيانات" description={error} onRetry={() => void loadFiles()} /> : null}

          {loading ? (
            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
              {Array.from({ length: 4 }).map((_, index) => (
                <LoadingSkeleton key={index} className="min-h-[176px] rounded-2xl" />
              ))}
            </div>
          ) : (
            <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4 xl:gap-5">
              {kpis.map((kpi, index) => {
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
            <DashboardSectionHeader dense title="رفع البيانات" description="ارفع ملف Procurement_Q2.xlsx أو أي ملف مالي مدعوم" />
            <UploadDataPanel disabled={uploading} onUpload={() => undefined} onFileUpload={(file) => void handleFileUpload(file)} />
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader dense title="الملفات المرفوعة" description="مجموعات البيانات المالية المتاحة للتحليل والتقارير" />
            {loading ? (
              <LoadingSkeleton className="min-h-[280px] rounded-2xl" />
            ) : (
              <UploadedFilesTable files={files} />
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader dense title="ملخص جودة البيانات" description="نتائج التحقق من الملفات المستوردة" />
            <DataSummaryCards validationItems={dataValidationSummary} />
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader dense title="سجل الاستيراد" description="تاريخ عمليات الاستيراد المرتبطة بالملفات" />
            <ImportHistoryTable
              items={files.map((file) => ({
                date: file.uploadDate,
                file: file.fileName,
                records: "—",
                status: file.status.includes("فشل") ? "فشل" : file.status.includes("قيد") ? "قيد المعالجة" : "نجح",
              }))}
            />
          </section>
        </div>
      </PageContainer>
    </AppLayout>
  );
}
