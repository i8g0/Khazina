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
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PageHero } from "@/components/ui/page-hero";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavItems,
} from "@/lib/app-nav";
import type { UploadedFileItem, DataValidationItem, ImportHistoryItem } from "@/lib/placeholder-data";
import {
  useRequireAuth,
  formatApiError,
  useOrganizationDisplay,
} from "@/lib/auth/auth-context";
import {
  getLatestQualitySnapshot,
  listFinancialFiles,
  listImportRecords,
  listQualityChecks,
  uploadFinancialFile,
} from "@/lib/api/khazina-api";
import { writeDemoArtifacts } from "@/lib/demo/state";
import { formatDate, mapProcessingStatus } from "@/lib/format";

const summaryIcons = [FileStack, Database, HardDrive, FileCheck2];

export function DataManagementPage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const [loading, setLoading] = React.useState(true);
  const [uploading, setUploading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [files, setFiles] = React.useState<UploadedFileItem[]>([]);
  const [importHistory, setImportHistory] = React.useState<ImportHistoryItem[]>([]);
  const [validationItems, setValidationItems] = React.useState<DataValidationItem[]>([]);
  const [qualityScore, setQualityScore] = React.useState<string>("—");
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
      const mapped: UploadedFileItem[] = rows.map((row) => ({
        id: row.id,
        fileName: row.file_name,
        department: "—",
        uploadDate: formatDate(row.uploaded_at),
        size: row.size_display ?? "—",
        status: mapProcessingStatus(row.processing_status),
      }));
      setFiles(mapped);

      const latestFile = rows[0];
      if (latestFile) {
        const records = await listImportRecords(
          auth.session.organizationId,
          auth.session.token,
          latestFile.id,
        );
        setImportHistory(
          records.map((record) => ({
            date: formatDate(record.imported_at),
            file: latestFile.file_name,
            records:
              record.record_count != null ? String(record.record_count) : "—",
            status:
              record.status === "failed" || record.status.includes("fail")
                ? "فشل"
                : record.status.includes("process")
                  ? "قيد المعالجة"
                  : "نجح",
          })),
        );
      } else {
        setImportHistory([]);
      }

      const snapshot = await getLatestQualitySnapshot(
        auth.session.organizationId,
        auth.session.token,
      );
      if (snapshot) {
        setQualityScore(
          snapshot.overall_score != null
            ? `${snapshot.overall_score.toFixed(1)}%`
            : "—",
        );
        const checks = await listQualityChecks(
          auth.session.organizationId,
          auth.session.token,
          snapshot.id,
        );
        setValidationItems(
          checks
            .slice()
            .sort((a, b) => a.display_order - b.display_order)
            .map((check) => ({
              check: check.check_name,
              result: `${check.result_percent.toFixed(1)}%`,
              details: check.details ?? "—",
            })),
        );
      } else {
        setQualityScore("—");
        setValidationItems([]);
      }
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
      setUploadMessage(
        `تم رفع ${file.name} — الحالة: ${mapProcessingStatus(outcome.financial_file.processing_status)}`,
      );
      await loadFiles();
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setUploading(false);
    }
  };

  const readyCount = files.filter(
    (f) => f.status.includes("جاهز") || f.status.includes("مكتمل"),
  ).length;

  const kpis = [
    { label: "الملفات المرفوعة", value: String(files.length), hint: "مستودع البيانات" },
    { label: "جاهزة للتحليل", value: String(readyCount), hint: "حالة المعالجة" },
    { label: "آخر رفع", value: files[0]?.uploadDate ?? "—", hint: files[0]?.fileName ?? "لا يوجد" },
    { label: "جودة البيانات", value: qualityScore, hint: "آخر تقييم محفوظ" },
  ];

  if (!auth.session) {
    return null;
  }

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="مستودع البيانات"
      subtitle={org.reportingPeriod}
      activeItemId="data"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="مستودع البيانات المالية"
            description={`${org.name} — إدارة مجموعات البيانات المؤسسية.`}
            period={org.reportingPeriod}
          />

          {uploadMessage ? (
            <Alert variant="success" title="تم تحديث المستودع">
              {uploadMessage}
            </Alert>
          ) : null}

          {error ? (
            <ErrorState
              title="تعذّر تحميل البيانات"
              description={error}
              onRetry={() => void loadFiles()}
            />
          ) : null}

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
            <DashboardSectionHeader
              dense
              title="رفع البيانات"
              description={uploading ? "جاري الرفع والمعالجة..." : "ارفع ملف Excel أو CSV مدعوم"}
            />
            <UploadDataPanel
              disabled={uploading}
              onUpload={() => undefined}
              onFileUpload={(file) => void handleFileUpload(file)}
            />
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="الملفات المرفوعة"
              description="مجموعات البيانات المالية المتاحة للتحليل والتقارير"
            />
            {loading ? (
              <LoadingSkeleton className="min-h-[280px] rounded-2xl" />
            ) : files.length === 0 ? (
              <EmptyState
                title="لا توجد ملفات"
                description="ارفع أول ملف مالي لبدء التحليل"
              />
            ) : (
              <UploadedFilesTable files={files} />
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="ملخص جودة البيانات"
              description="نتائج التحقق من آخر لقطة جودة محفوظة"
            />
            {loading ? (
              <LoadingSkeleton className="min-h-[160px] rounded-2xl" />
            ) : validationItems.length === 0 ? (
              <EmptyState
                title="لا توجد فحوصات جودة"
                description="ستظهر نتائج فحوصات الجودة بعد اكتمال الاستيراد والتقييم"
              />
            ) : (
              <DataSummaryCards validationItems={validationItems} />
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="سجل الاستيراد"
              description="عمليات الاستيراد المرتبطة بآخر ملف"
            />
            {loading ? (
              <LoadingSkeleton className="min-h-[200px] rounded-2xl" />
            ) : importHistory.length === 0 ? (
              <EmptyState
                title="لا يوجد سجل استيراد"
                description="سيظهر السجل بعد رفع ملف وحفظ سجلات الاستيراد"
              />
            ) : (
              <ImportHistoryTable items={importHistory} />
            )}
          </section>
        </div>
      </PageContainer>
    </AppLayout>
  );
}
