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
  getAppNavGroups,
} from "@/lib/app-nav";
import { WorkflowIndicator } from "@/components/workflow/workflow-indicator";
import { OperationLoadingPanel } from "@/components/workflow/operation-loading-panel";
import { AnalysisCompletionPanel } from "@/components/workflow/analysis-completion-panel";
import { AuthLoadingShell } from "@/components/workflow/auth-loading-shell";
import type { ReportItem } from "@/lib/placeholder-data";
import {
  useRequireAuth,
  formatApiError,
} from "@/lib/auth/auth-context";
import { useOrganizationDisplay, useOrgLookups } from "@/lib/org-lookups";
import {
  downloadReportPdf,
  generateReport,
  getReportContent,
  listReports,
} from "@/lib/api/khazina-api";
import { writeDemoArtifacts } from "@/lib/demo/state";
import { useDemoArtifacts } from "@/lib/demo/hooks";
import { formatDate, mapReportStatus, mapReportType, sanitizeExecutiveText } from "@/lib/format";
import {
  canExportPdf,
  REPORT_TITLES,
  resolveExportReportId,
} from "@/lib/reports/report-export";
import { cn } from "@/lib/utils";

function extractPreviewText(
  summary: string,
  content?: { sections?: { key: string; payload: Record<string, unknown> }[] },
): string {
  const executive = content?.sections?.find((s) => s.key === "executive_summary");
  const text = executive?.payload?.text;
  if (typeof text === "string" && text.trim()) {
    return sanitizeExecutiveText(text);
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
    department_id?: string | null;
    source_file_id?: string | null;
    analysis_run_id?: string | null;
    has_content?: boolean;
  },
  previewText: string,
  resolveDepartment: (id: string | null | undefined) => string | null,
  resolveFile: (id: string | null | undefined) => string | null,
): ReportItem {
  return {
    id: row.id,
    title: row.title,
    type: mapReportType(row.report_type),
    department: row.department_id
      ? resolveDepartment(row.department_id) ?? "قسم غير معروف"
      : "بدون قسم",
    sourceFile: row.source_file_id
      ? resolveFile(row.source_file_id) ?? "ملف غير معروف"
      : "لا يوجد ملف مصدر",
    date: row.created_at,
    status: mapReportStatus(row.status),
    previewText,
    analysisRunId: row.analysis_run_id ?? null,
    hasContent: row.has_content ?? false,
  };
}

export function ReportsPage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const artifacts = useDemoArtifacts();
  const { departments, departmentName, fileName } = useOrgLookups();
  const [loading, setLoading] = React.useState(true);
  const [generating, setGenerating] = React.useState(false);
  const [exporting, setExporting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [reports, setReports] = React.useState<ReportItem[]>([]);
  const [typeFilter, setTypeFilter] = React.useState("الكل");
  const [departmentFilter, setDepartmentFilter] = React.useState("الكل");
  const [showCompletion, setShowCompletion] = React.useState(false);
  const [selectedReportId, setSelectedReportId] = React.useState<string | null>(null);
  const reportsSectionRef = React.useRef<HTMLElement>(null);

  const exportCandidates = React.useMemo(
    () =>
      reports.map((report) => ({
        id: report.id,
        analysisRunId: report.analysisRunId ?? null,
        hasContent: report.hasContent ?? false,
      })),
    [reports],
  );

  const resolvedExportReportId = React.useMemo(
    () => resolveExportReportId(exportCandidates, artifacts, selectedReportId),
    [exportCandidates, artifacts, selectedReportId],
  );

  const pdfExportEnabled = canExportPdf(
    exportCandidates,
    artifacts,
    selectedReportId,
  );

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
          return toReportItem(row, preview, departmentName, fileName);
        }),
      );
      setReports(mapped);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session, departmentName, fileName]);

  React.useEffect(() => {
    if (auth.session) void loadReports();
  }, [auth.session, loadReports]);

  const handleGenerate = async (
    runId: string,
    label: string,
    title: string,
  ) => {
    if (!auth.session) return;
    setGenerating(true);
    setError(null);
    try {
      const outcome = await generateReport(
        auth.session.organizationId,
        auth.session.token,
        runId,
        title,
      );
      writeDemoArtifacts({ lastReportId: outcome.report.id });
      setSelectedReportId(outcome.report.id);
      setMessage(`تم إنشاء ${label}`);
      setShowCompletion(true);
      await loadReports();
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateWaste = () => {
    if (!artifacts.wasteRunId) {
      setError("شغّل تحليل الهدر أولاً قبل إنشاء التقرير");
      return;
    }
    void handleGenerate(
      artifacts.wasteRunId,
      "تقرير الهدر",
      REPORT_TITLES.waste,
    );
  };

  const handleGenerateRisk = () => {
    if (!artifacts.riskRunId) {
      setError("شغّل تحليل المخاطر أولاً قبل إنشاء التقرير");
      return;
    }
    void handleGenerate(
      artifacts.riskRunId,
      "تقرير المخاطر",
      REPORT_TITLES.risk,
    );
  };

  const handleGenerateSimulation = () => {
    if (!artifacts.simulationAnalysisRunId) {
      setError("شغّل محاكاة السيناريو أولاً قبل إنشاء التقرير");
      return;
    }
    void handleGenerate(
      artifacts.simulationAnalysisRunId,
      "تقرير المحاكاة",
      REPORT_TITLES.simulation,
    );
  };

  const handlePdfExport = async (reportIdOverride?: string) => {
    if (!auth.session) return;
    const reportId =
      reportIdOverride ?? resolvedExportReportId ?? artifacts.lastReportId;
    if (!reportId) {
      setError(
        "لا يوجد تقرير جاهز للتصدير — أنشئ تقريراً من تحليل الهدر أو المخاطر أو المحاكاة",
      );
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
      const selected = reports.find((row) => row.id === reportId);
      const safeTitle = (selected?.title ?? "khazina-report")
        .replace(/[^\w\u0600-\u06FF\s-]+/g, "")
        .trim()
        .replace(/\s+/g, "-")
        .slice(0, 80);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${safeTitle || "khazina-report"}.pdf`;
      anchor.click();
      URL.revokeObjectURL(url);
      setSelectedReportId(reportId);
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

  const departmentFilterOptions = React.useMemo(
    () => ["الكل", ...departments.map((dept) => dept.name_ar)],
    [departments],
  );

  const readyCount = reports.filter((r) => r.status === "جاهز").length;

  React.useEffect(() => {
    if (
      departmentFilter !== "الكل" &&
      !departmentFilterOptions.includes(departmentFilter)
    ) {
      setDepartmentFilter("الكل");
    }
  }, [departmentFilter, departmentFilterOptions]);

  if (auth.isLoading) return <AuthLoadingShell />;
  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="التقارير"
      subtitle={org.reportingPeriod ?? undefined}
      activeItemId="reports"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="التقارير"
            description="إنشاء وتصدير التقارير التنفيذية لمراجعة نتائج التحليل المالي."
            period={org.reportingPeriod}
          />

          <WorkflowIndicator activeStageId="report" />

          {showCompletion ? (
            <AnalysisCompletionPanel
              onViewReport={() =>
                reportsSectionRef.current?.scrollIntoView({ behavior: "smooth" })
              }
              onExportPdf={() => void handlePdfExport()}
              pdfExporting={exporting}
            />
          ) : null}

          <div className="flex flex-wrap gap-3">
            <Button disabled={generating} onClick={() => void handleGenerateWaste()}>
              {generating ? "جاري إنشاء التقرير..." : "إنشاء تقرير من تحليل الهدر"}
            </Button>
            <Button
              variant="outline"
              disabled={generating || !artifacts.riskRunId}
              onClick={() => void handleGenerateRisk()}
            >
              إنشاء تقرير من تحليل المخاطر
            </Button>
            <Button
              variant="outline"
              disabled={generating || !artifacts.simulationAnalysisRunId}
              onClick={() => void handleGenerateSimulation()}
            >
              إنشاء تقرير من المحاكاة
            </Button>
          </div>

          {generating ? (
            <OperationLoadingPanel
              title="جاري إنشاء التقرير التنفيذي"
              description="تجميع نتائج التحليل والتوصيات في تقرير جاهز للمراجعة."
            />
          ) : null}

          {message ? <Alert variant="success" title="تم">{message}</Alert> : null}
          {error ? (
            <ErrorState
              title="تعذّر إكمال العملية"
              description={error}
              onRetry={() => setError(null)}
            />
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
                value={
                  reports[0]
                    ? formatDate(reports[0].date)
                    : "لا توجد تقارير بعد"
                }
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
                options={departmentFilterOptions}
                value={departmentFilter}
                onChange={setDepartmentFilter}
              />
            </div>
          </section>

          <section ref={reportsSectionRef} className={executiveSectionSpacingClassName}>
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
                  <ReportsCard
                    key={report.id}
                    report={report}
                    selected={selectedReportId === report.id}
                    onSelect={() => setSelectedReportId(report.id)}
                    onExportPdf={() => void handlePdfExport(report.id)}
                    pdfExporting={exporting && resolvedExportReportId === report.id}
                  />
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
              pdfEnabled={pdfExportEnabled}
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
