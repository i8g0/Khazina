"use client";

import * as React from "react";
import Link from "next/link";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { Input } from "@/components/ui/input";
import { PageFeedback } from "@/components/ui/page-feedback";
import { PageHero } from "@/components/ui/page-hero";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavItems,
} from "@/lib/app-nav";
import {
  activateReportingPeriod,
  closeActiveReportingPeriod,
  createDepartment,
  createReportingPeriod,
  deactivateDepartment,
  getOrganization,
  listDepartments,
  listReportingPeriods,
  patchOrganization,
  reactivateDepartment,
} from "@/lib/api/khazina-api";
import type {
  DepartmentResponse,
  ReportingPeriodResponse,
} from "@/lib/api/types";
import {
  formatApiError,
  useAuth,
  useOrganizationDisplay,
  useRequireAuth,
} from "@/lib/auth/auth-context";
import { formatDate } from "@/lib/format";

export function OrganizationManagementPage() {
  const auth = useRequireAuth();
  const { updateSession } = useAuth();
  const org = useOrganizationDisplay();
  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [name, setName] = React.useState("");
  const [platformName, setPlatformName] = React.useState("");
  const [executiveTitle, setExecutiveTitle] = React.useState("");
  const [departments, setDepartments] = React.useState<DepartmentResponse[]>([]);
  const [periods, setPeriods] = React.useState<ReportingPeriodResponse[]>([]);
  const [deptName, setDeptName] = React.useState("");
  const [deptCode, setDeptCode] = React.useState("");
  const [periodLabel, setPeriodLabel] = React.useState("");

  const load = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    try {
      const [organization, deptRows, periodRows] = await Promise.all([
        getOrganization(auth.session.organizationId, auth.session.token),
        listDepartments(auth.session.organizationId, auth.session.token, {
          limit: 100,
        }),
        listReportingPeriods(auth.session.organizationId, auth.session.token, {
          limit: 100,
        }),
      ]);
      setName(organization.name);
      setPlatformName(organization.platform_name);
      setExecutiveTitle(organization.executive_title ?? "");
      setDepartments(deptRows);
      setPeriods(periodRows);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session]);

  React.useEffect(() => {
    if (auth.session) void load();
  }, [auth.session, load]);

  const saveIdentity = async () => {
    if (!auth.session) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await patchOrganization(
        auth.session.organizationId,
        auth.session.token,
        {
          name: name.trim(),
          platform_name: platformName.trim(),
          executive_title: executiveTitle.trim() || null,
        },
      );
      updateSession({
        organizationName: updated.name,
        platformName: updated.platform_name,
        executiveTitle: updated.executive_title,
      });
      setMessage("تم تحديث هوية المؤسسة");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const addDepartment = async () => {
    if (!auth.session || !deptName.trim()) {
      setError("أدخل اسم القسم");
      return;
    }
    try {
      await createDepartment(auth.session.organizationId, auth.session.token, {
        name_ar: deptName.trim(),
        code: deptCode.trim() || null,
      });
      setDeptName("");
      setDeptCode("");
      setMessage("تم إنشاء القسم");
      await load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  const toggleDepartment = async (row: DepartmentResponse) => {
    if (!auth.session) return;
    try {
      if (row.is_active) {
        await deactivateDepartment(
          auth.session.organizationId,
          auth.session.token,
          row.id,
        );
        setMessage("تم تعطيل القسم");
      } else {
        await reactivateDepartment(
          auth.session.organizationId,
          auth.session.token,
          row.id,
        );
        setMessage("تم إعادة تفعيل القسم");
      }
      await load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  const addPeriod = async () => {
    if (!auth.session || !periodLabel.trim()) {
      setError("أدخل تسمية الفترة");
      return;
    }
    try {
      await createReportingPeriod(
        auth.session.organizationId,
        auth.session.token,
        { label: periodLabel.trim(), activate: false },
      );
      setPeriodLabel("");
      setMessage("تم إنشاء الفترة");
      await load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  const activatePeriod = async (periodId: string) => {
    if (!auth.session) return;
    try {
      await activateReportingPeriod(
        auth.session.organizationId,
        auth.session.token,
        periodId,
      );
      setMessage("تم تفعيل الفترة");
      await load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  const closeActive = async () => {
    if (!auth.session) return;
    try {
      await closeActiveReportingPeriod(
        auth.session.organizationId,
        auth.session.token,
      );
      setMessage("تم إغلاق الفترة النشطة");
      await load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="إدارة المؤسسة"
      subtitle={org.reportingPeriod}
      activeItemId="organization"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="إدارة المؤسسة"
            description="هوية المؤسسة والأقسام وفترات التقارير ضمن المؤسسة النشطة."
            period={org.reportingPeriod}
          />

          <p className="text-sm text-muted">
            إعدادات التشغيل والذكاء الاصطناعي في{" "}
            <Link href="/settings" className="text-gold-dark underline">
              الإعدادات
            </Link>
            . إدارة المستخدمين في{" "}
            <Link href="/users" className="text-gold-dark underline">
              المستخدمون
            </Link>
            .
          </p>

          <PageFeedback
            loading={loading}
            error={error}
            message={message}
            onRetry={() => void load()}
          >
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="هوية المؤسسة" />
              <div className="grid gap-4 rounded-2xl border border-border/60 bg-surface p-5 md:grid-cols-3">
                <label className="space-y-1.5 text-sm">
                  <span className="text-muted">اسم المؤسسة</span>
                  <Input
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                  />
                </label>
                <label className="space-y-1.5 text-sm">
                  <span className="text-muted">اسم المنصة</span>
                  <Input
                    value={platformName}
                    onChange={(event) => setPlatformName(event.target.value)}
                  />
                </label>
                <label className="space-y-1.5 text-sm">
                  <span className="text-muted">المسمى التنفيذي</span>
                  <Input
                    value={executiveTitle}
                    onChange={(event) => setExecutiveTitle(event.target.value)}
                  />
                </label>
                <div className="md:col-span-3">
                  <Button
                    type="button"
                    disabled={saving}
                    onClick={() => void saveIdentity()}
                  >
                    {saving ? "جاري الحفظ..." : "حفظ الهوية"}
                  </Button>
                </div>
              </div>
            </section>

            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="الأقسام" />
              <div className="mb-4 flex flex-wrap gap-3">
                <Input
                  className="max-w-xs"
                  placeholder="اسم القسم"
                  value={deptName}
                  onChange={(event) => setDeptName(event.target.value)}
                />
                <Input
                  className="max-w-[160px]"
                  placeholder="الرمز"
                  value={deptCode}
                  onChange={(event) => setDeptCode(event.target.value)}
                />
                <Button type="button" onClick={() => void addDepartment()}>
                  إضافة قسم
                </Button>
              </div>
              <DataTable
                data={departments}
                emptyMessage="لا توجد أقسام"
                columns={[
                  {
                    key: "name",
                    header: "الاسم",
                    cell: (row) => row.name_ar,
                  },
                  {
                    key: "code",
                    header: "الرمز",
                    cell: (row) => row.code ?? "—",
                  },
                  {
                    key: "status",
                    header: "الحالة",
                    cell: (row) =>
                      row.is_active ? (
                        <Badge variant="outline">نشط</Badge>
                      ) : (
                        <Badge variant="outline">معطّل</Badge>
                      ),
                  },
                  {
                    key: "actions",
                    header: "إجراء",
                    cell: (row) => (
                      <Button
                        type="button"
                        size="sm"
                        variant="secondary"
                        onClick={() => void toggleDepartment(row)}
                      >
                        {row.is_active ? "تعطيل" : "تفعيل"}
                      </Button>
                    ),
                  },
                ]}
              />
            </section>

            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="فترات التقارير" />
              <div className="mb-4 flex flex-wrap gap-3">
                <Input
                  className="max-w-xs"
                  placeholder="تسمية الفترة"
                  value={periodLabel}
                  onChange={(event) => setPeriodLabel(event.target.value)}
                />
                <Button type="button" onClick={() => void addPeriod()}>
                  إنشاء فترة
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => void closeActive()}
                >
                  إغلاق الفترة النشطة
                </Button>
              </div>
              <DataTable
                data={periods}
                emptyMessage="لا توجد فترات"
                columns={[
                  {
                    key: "label",
                    header: "التسمية",
                    cell: (row) => row.label,
                  },
                  {
                    key: "dates",
                    header: "المدى",
                    cell: (row) =>
                      `${row.start_date ? formatDate(row.start_date) : "—"} → ${
                        row.end_date ? formatDate(row.end_date) : "—"
                      }`,
                  },
                  {
                    key: "status",
                    header: "الحالة",
                    cell: (row) =>
                      row.is_active ? (
                        <Badge variant="outline">نشطة</Badge>
                      ) : (
                        <Badge variant="outline">مغلقة</Badge>
                      ),
                  },
                  {
                    key: "actions",
                    header: "إجراء",
                    cell: (row) =>
                      row.is_active ? (
                        "—"
                      ) : (
                        <Button
                          type="button"
                          size="sm"
                          variant="secondary"
                          onClick={() => void activatePeriod(row.id)}
                        >
                          تفعيل
                        </Button>
                      ),
                  },
                ]}
              />
            </section>
          </PageFeedback>
        </div>
      </PageContainer>
    </AppLayout>
  );
}
