"use client";

import * as React from "react";
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
  getAppNavGroups,
} from "@/lib/app-nav";
import { EXECUTIVE_MESSAGES } from "@/lib/workflow/messages";
import {
  createUser,
  deactivateUser,
  listUsers,
  patchUser,
} from "@/lib/api/khazina-api";
import type { UserResponse } from "@/lib/api/types";
import {
  formatApiError,
  useOrganizationDisplay,
  useRequireAuth,
} from "@/lib/auth/auth-context";
import { formatDate } from "@/lib/format";
import { AuthLoadingShell } from "@/components/workflow/auth-loading-shell";

const PAGE_SIZE = 50;
const ROLES: UserResponse["role"][] = ["admin", "executive", "analyst"];

const roleLabel: Record<UserResponse["role"], string> = {
  admin: "مسؤول",
  executive: "تنفيذي",
  analyst: "محلل",
};

export function UsersManagementPage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [activeOnly, setActiveOnly] = React.useState(false);
  const [users, setUsers] = React.useState<UserResponse[]>([]);
  const [fullName, setFullName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [role, setRole] = React.useState<UserResponse["role"]>("analyst");
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [editName, setEditName] = React.useState("");
  const [editEmail, setEditEmail] = React.useState("");
  const [editRole, setEditRole] = React.useState<UserResponse["role"]>("analyst");

  const load = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    try {
      const rows = await listUsers(auth.session.organizationId, auth.session.token, {
        active_only: activeOnly,
        limit: PAGE_SIZE,
        offset: 0,
      });
      setUsers(rows);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session, activeOnly]);

  React.useEffect(() => {
    if (auth.session) void load();
  }, [auth.session, load]);

  const handleCreate = async () => {
    if (!auth.session) return;
    if (!fullName.trim() || !email.trim() || password.length < 8) {
      setError("الاسم والبريد وكلمة مرور (8 أحرف على الأقل) مطلوبة");
      return;
    }
    try {
      await createUser(auth.session.organizationId, auth.session.token, {
        full_name: fullName.trim(),
        email: email.trim(),
        password,
        role,
      });
      setFullName("");
      setEmail("");
      setPassword("");
      setRole("analyst");
      setMessage("تم إنشاء المستخدم");
      await load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  const startEdit = (user: UserResponse) => {
    setEditingId(user.id);
    setEditName(user.full_name);
    setEditEmail(user.email);
    setEditRole(user.role);
  };

  const saveEdit = async () => {
    if (!auth.session || !editingId) return;
    try {
      await patchUser(auth.session.organizationId, auth.session.token, editingId, {
        full_name: editName.trim(),
        email: editEmail.trim(),
        role: editRole,
      });
      setEditingId(null);
      setMessage("تم تحديث المستخدم");
      await load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  const handleDeactivate = async (userId: string) => {
    if (!auth.session) return;
    try {
      await deactivateUser(
        auth.session.organizationId,
        auth.session.token,
        userId,
      );
      setMessage("تم تعطيل المستخدم");
      await load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  if (auth.isLoading) return <AuthLoadingShell />;
  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="إدارة المستخدمين"
      subtitle={org.reportingPeriod}
      activeItemId="users"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="إدارة المستخدمين"
            description="إنشاء وتعديل وتعطيل مستخدمي المؤسسة (مسؤولو المؤسسة)."
            period={org.reportingPeriod}
          />

          <div className="flex flex-wrap gap-3">
            <Button
              type="button"
              variant={!activeOnly ? "primary" : "secondary"}
              onClick={() => setActiveOnly(false)}
              aria-pressed={!activeOnly}
            >
              الكل
            </Button>
            <Button
              type="button"
              variant={activeOnly ? "primary" : "secondary"}
              onClick={() => setActiveOnly(true)}
              aria-pressed={activeOnly}
            >
              النشطون فقط
            </Button>
          </div>

          <PageFeedback
            loading={loading}
            error={error}
            message={message}
            empty={
              !loading && users.length === 0
                ? {
                    title: "لا يوجد مستخدمون",
                    description: "أنشئ مستخدمًا جديدًا أو ألغِ تصفية النشطين.",
                  }
                : null
            }
            onRetry={() => void load()}
          >
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="مستخدم جديد" />
              <div className="grid gap-3 rounded-2xl border border-border/60 bg-surface p-5 md:grid-cols-2 xl:grid-cols-5">
                <Input
                  placeholder="الاسم الكامل"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  aria-label="الاسم الكامل"
                />
                <Input
                  type="email"
                  placeholder="البريد"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  aria-label="البريد"
                />
                <Input
                  type="password"
                  placeholder="كلمة المرور"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  aria-label="كلمة المرور"
                />
                <select
                  className="h-10 rounded-lg border border-border bg-surface px-3 text-sm"
                  value={role}
                  onChange={(event) =>
                    setRole(event.target.value as UserResponse["role"])
                  }
                  aria-label="الدور"
                >
                  {ROLES.map((value) => (
                    <option key={value} value={value}>
                      {roleLabel[value]}
                    </option>
                  ))}
                </select>
                <Button type="button" onClick={() => void handleCreate()}>
                  إنشاء
                </Button>
              </div>
            </section>

            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="قائمة المستخدمين" />
              <DataTable
                data={users}
                emptyMessage="لا يوجد مستخدمون"
                columns={[
                  {
                    key: "name",
                    header: "الاسم",
                    cell: (row) =>
                      editingId === row.id ? (
                        <Input
                          value={editName}
                          onChange={(event) => setEditName(event.target.value)}
                          aria-label="تعديل الاسم"
                        />
                      ) : (
                        row.full_name
                      ),
                  },
                  {
                    key: "email",
                    header: "البريد",
                    cell: (row) =>
                      editingId === row.id ? (
                        <Input
                          value={editEmail}
                          onChange={(event) => setEditEmail(event.target.value)}
                          aria-label="تعديل البريد"
                        />
                      ) : (
                        row.email
                      ),
                  },
                  {
                    key: "role",
                    header: "الدور",
                    cell: (row) =>
                      editingId === row.id ? (
                        <select
                          className="h-10 rounded-lg border border-border bg-surface px-2 text-sm"
                          value={editRole}
                          onChange={(event) =>
                            setEditRole(
                              event.target.value as UserResponse["role"],
                            )
                          }
                          aria-label="تعديل الدور"
                        >
                          {ROLES.map((value) => (
                            <option key={value} value={value}>
                              {roleLabel[value]}
                            </option>
                          ))}
                        </select>
                      ) : (
                        roleLabel[row.role]
                      ),
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
                    key: "created",
                    header: "أُنشئ",
                    cell: (row) => formatDate(row.created_at),
                  },
                  {
                    key: "actions",
                    header: "إجراءات",
                    cell: (row) => (
                      <div className="flex flex-wrap gap-2">
                        {editingId === row.id ? (
                          <>
                            <Button
                              type="button"
                              size="sm"
                              onClick={() => void saveEdit()}
                            >
                              حفظ
                            </Button>
                            <Button
                              type="button"
                              size="sm"
                              variant="secondary"
                              onClick={() => setEditingId(null)}
                            >
                              إلغاء
                            </Button>
                          </>
                        ) : (
                          <>
                            <Button
                              type="button"
                              size="sm"
                              variant="secondary"
                              disabled={!row.is_active}
                              onClick={() => startEdit(row)}
                            >
                              تعديل
                            </Button>
                            <Button
                              type="button"
                              size="sm"
                              variant="outline"
                              disabled={!row.is_active}
                              onClick={() => void handleDeactivate(row.id)}
                            >
                              تعطيل
                            </Button>
                          </>
                        )}
                      </div>
                    ),
                  },
                ]}
              />
              <p className="text-sm text-muted">
                {EXECUTIVE_MESSAGES.usersApiLimit}
              </p>
            </section>
          </PageFeedback>
        </div>
      </PageContainer>
    </AppLayout>
  );
}
