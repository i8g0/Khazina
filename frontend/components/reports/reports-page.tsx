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
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
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
import { organization } from "@/lib/placeholder-data";
import type { ReportItem } from "@/lib/placeholder-data";
import { useRequireAuth, formatApiError } from "@/lib/auth/auth-context";
import {
  downloadReportPdf,
  generateReport,
  getReportContent,
  listReports,
} from "@/lib/api/khazina-api";
import { readDemoArtifacts, writeDemoArtifacts } from "@/lib/demo/state";
import { formatDate, mapReportStatus, mapReportType } from "@/lib/format";
import { cn } from "@/lib/utils";

function extractPreviewText(
  summary: string,
  content?: { sections?: { key: string; payload: Record<string, unknown> }[] },
): string {
  const executive = content?.sections?.find((s) => s.key === "executive_summary");
  const text = executive?.payload?.text;
  if (typeof text === "string" && text.trim()) {
    return text;
  }
  return summary;
}

function toReportItem(
  row: {
    id: string;
    title: string;
    report_type: string;
    status: string;
    summary: string;
    created_at: string;
  },
  previewText: string,
): ReportItem {
  return {
    id: row.id,
    title: row.title,
    type: mapReportType(row.report_type),
    department: "الشؤون المالية",
    sourceFile: "Procurement_Q2.xlsx",
    date: row.created_at,
    status: mapReportStatus(row.status),
    previewText,
  };
}

export function ReportsPage() {
  const auth = useRequireAuth();
  const [loading, setLoading] = React.useState(true);
  const [generating, setGenerating] = React.useState(false);
  const [exporting, setExporting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [reports, setReports] = React.useState<ReportItem[]>([]);
  const [typeFilter, setTypeFilter] = React.useState("الكل");
  const [departmentFilter, setDepartmentFilter] = React.useState("الكل");

  const loadReports = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    try {
      const rows = await listReports(auth.session.organizationId, auth.session.token);
      const mapped = await Promise.all(
        rows.map(async (row) => {
          let preview = row.summary;
          if (row.has_content) {
            try {
              const content = await getReportContent(
                auth.session!.organizationId,
                auth.session!.token,
                row.id,
              );
              preview = extractPreviewText(row.summary, content.content);
            } catch {
              preview = row.summary;
            }
          }
          return toReportItem(row, preview);
        }),
      );
      setReports(mapped);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session]);

  React.useEffect(() => {
    if (auth.session) void loadReports();
  }, [auth.session, loadReports]);

  const handleGenerate = async () => {
    if (!auth.session) return;
    const artifacts = readDemoArtifacts();
    if (!artifacts.wasteRunId) {
      setError("شغّل تحليل الهدر أولاً قبل إنشاء التقرير");
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      const outcome = await generateReport(
        auth.session.organizationId,
        auth.session.token,
        artifacts.wasteRunId,
      );
      writeDemoArtifacts({ lastReportId: outcome.report.id });
      setMessage("تم إنشاء التقرير التنفيذي");
      await loadReports();
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setGenerating(false);
    }
  };

  const handlePdfExport = async () => {
    if (!auth.session) return;
    const reportId =
      readDemoArtifacts().lastReportId ?? reports.find((r) => r.status === "جاهز")?.id;
    if (!reportId) {
      setError("لا يوجد تقرير جاهز للتصدير — أنشئ تقريراً أولاً");
      return;
    }
    setExporting(true);
    setError(null);
    try {
      const blob = await downloadReportPdf(
        auth.session.organizationId,
        auth.session.token,
        reportId,
      );
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "khazina-report.pdf";
      anchor.click();
      URL.revokeObjectURL(url);
      setMessage("تم تنزيل ملف PDF");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setExporting(false);
    }
  };

  const filteredReports = React.useMemo(() => {
    return reports.filter((report) => {
      const typeMatch = typeFilter === "الكل" || report.type === typeFilter;
      const deptMatch =
        departmentFilter === "الكل" || report.department === departmentFilter;
      return typeMatch && deptMatch;
    });
  }, [reports, typeFilter, departmentFilter]);

  const readyCount = reports.filter((r) => r.status === "جاهز").length;

  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="التقارير"
      subtitle={organization.reportingPeriod}
      activeItemId="reports"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="التقارير"
            description="عرض وتصفية وتصدير التقارير المالية والتحليلية للمراجعة التنفيذية."
            period={organization.reportingPeriod}
          />

          <div className="flex flex-wrap gap-3">
            <Button disabled={generating} onClick={() => void handleGenerate()}>
              {generating ? "جاري الإنشاء..." : "إنشاء تقرير من تحليل الهدر"}
            </Button>
          </div>

          {message ? <Alert variant="success" title="تم">{message}</Alert> : null}
          {error ? (
            <ErrorState title="خطأ" description={error} onRetry={() => setError(null)} />
          ) : null}

          {loading ? (
            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
              {Array.from({ length: 4 }).map((_, index) => (
                <LoadingSkeleton key={index} className="min-h-[188px] rounded-2xl" />
              ))}
            </div>
          ) : (
            <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4 xl:gap-5">
              <DashboardStatCard
                label="إجمالي التقارير"
                value={String(reports.length)}
                hint="في المؤسسة"
                emphasis
                dense
                icon={<Files className="h-[17px] w-[17px]" strokeWidth={1.75} />}
              />
              <DashboardStatCard
                label="جاهزة"
                value={String(readyCount)}
                hint="قابلة للتصدير"
                emphasis
                dense
                icon={<FileCheck2 className="h-[17px] w-[17px]" strokeWidth={1.75} />}
              />
              <DashboardStatCard
                label="مسودات"
                value={String(reports.length - readyCount)}
                hint="قيد الإعداد"
                emphasis
                dense
                icon={<FileClock className="h-[17px] w-[17px]" strokeWidth={1.75} />}
              />
              <DashboardStatCard
                label="آخر تحديث"
                value={reports[0] ? formatDate(reports[0].date) : "—"}
                hint="أحدث تقرير"
                emphasis
                dense
                icon={<FileBarChart className="h-[17px] w-[17px]" strokeWidth={1.75} />}
              />
            </section>
          )}

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="تصفية التقارير"
              description="تصفية حسب النوع والقسم"
            />
            <div className="flex flex-wrap gap-5 rounded-2xl border border-border/60 bg-surface px-5 py-5 md:px-6 md:py-5">
              <FilterGroup
                label="النوع"
                options={["الكل", "تحليل", "مخاطر", "محاكاة"]}
                value={typeFilter}
                onChange={setTypeFilter}
              />
              <FilterGroup
                label="القسم"
                options={["الكل", "الشؤون المالية"]}
                value={departmentFilter}
                onChange={setDepartmentFilter}
              />
            </div>
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="التقارير المُنشأة"
              description="معاينة التقارير الجاهزة والمسودات"
            />
            {loading ? (
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 3 }).map((_, index) => (
                  <LoadingSkeleton key={index} className="min-h-[320px] rounded-2xl" />
                ))}
              </div>
            ) : filteredReports.length === 0 ? (
              <EmptyState
                title="لا توجد تقارير"
                description="سيتم إنشاء التقارير بعد إتمام التحليلات"
              />
            ) : (
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3 xl:gap-5">
                {filteredReports.map((report) => (
                  <ReportsCard key={report.id} report={report} />
                ))}
              </div>
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="سجل التقارير"
              description="سجل كامل للتقارير المُنشأة"
            />
            {loading ? (
              <LoadingSkeleton className="min-h-[320px] rounded-2xl" />
            ) : (
              <ReportsHistoryTable reports={filteredReports} />
            )}
          </section>

          <section className={executiveSectionSpacingClassName}>
            <ReportsExportPanel
              onPdfExport={() => void handlePdfExport()}
              pdfExporting={exporting}
              pdfEnabled={readyCount > 0}
            />
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
