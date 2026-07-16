"use client";

import * as React from "react";
import Link from "next/link";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageFeedback } from "@/components/ui/page-feedback";
import { PageHero } from "@/components/ui/page-hero";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavGroups,
} from "@/lib/app-nav";
import {
  getUnreadCount,
  getUserNotificationPreferences,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  patchUserNotificationPreferences,
} from "@/lib/api/khazina-api";
import type { NotificationResponse } from "@/lib/api/types";
import {
  formatApiError,
  useOrganizationDisplay,
  useRequireAuth,
} from "@/lib/auth/auth-context";
import { formatDate } from "@/lib/format";
import { cn } from "@/lib/utils";

const PAGE_SIZE = 20;

export function NotificationsCenterPage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [items, setItems] = React.useState<NotificationResponse[]>([]);
  const [unread, setUnread] = React.useState(0);
  const [unreadOnly, setUnreadOnly] = React.useState(false);
  const [offset, setOffset] = React.useState(0);
  const [hasMore, setHasMore] = React.useState(false);
  const [prefsEnabled, setPrefsEnabled] = React.useState(true);
  const [mutedKinds, setMutedKinds] = React.useState("");
  const [savingPrefs, setSavingPrefs] = React.useState(false);

  const load = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    try {
      const [rows, count, prefs] = await Promise.all([
        listNotifications(auth.session.organizationId, auth.session.token, {
          unread_only: unreadOnly,
          limit: PAGE_SIZE,
          offset,
        }),
        getUnreadCount(auth.session.organizationId, auth.session.token),
        getUserNotificationPreferences(
          auth.session.organizationId,
          auth.session.token,
        ),
      ]);
      setItems(rows);
      setHasMore(rows.length === PAGE_SIZE);
      setUnread(count);
      setPrefsEnabled(prefs.notifications_enabled);
      setMutedKinds(prefs.muted_notification_kinds.join(", "));
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session, unreadOnly, offset]);

  React.useEffect(() => {
    if (auth.session) void load();
  }, [auth.session, load]);

  const handleMarkRead = async (id: string) => {
    if (!auth.session) return;
    try {
      await markNotificationRead(
        auth.session.organizationId,
        auth.session.token,
        id,
      );
      setMessage("تم تعليم الإشعار كمقروء");
      await load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  const handleMarkAll = async () => {
    if (!auth.session) return;
    try {
      const marked = await markAllNotificationsRead(
        auth.session.organizationId,
        auth.session.token,
      );
      setMessage(`تم تعليم ${marked} إشعارًا كمقروء`);
      setOffset(0);
      await load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  const savePrefs = async () => {
    if (!auth.session) return;
    setSavingPrefs(true);
    setError(null);
    try {
      await patchUserNotificationPreferences(
        auth.session.organizationId,
        auth.session.token,
        {
          notifications_enabled: prefsEnabled,
          muted_notification_kinds: mutedKinds
            .split(",")
            .map((part) => part.trim())
            .filter(Boolean),
        },
      );
      setMessage("تم حفظ تفضيلات الإشعارات");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSavingPrefs(false);
    }
  };

  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="مركز الإشعارات"
      subtitle={org.reportingPeriod}
      activeItemId="notifications"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="مركز الإشعارات"
            description="متابعة الإشعارات غير المقروءة وإدارتها وتفضيلات الاستلام."
            period={org.reportingPeriod}
          />

          <div className="flex flex-wrap items-center gap-3">
            <Button
              type="button"
              variant={!unreadOnly ? "primary" : "secondary"}
              onClick={() => {
                setOffset(0);
                setUnreadOnly(false);
              }}
              aria-pressed={!unreadOnly}
            >
              الكل
            </Button>
            <Button
              type="button"
              variant={unreadOnly ? "primary" : "secondary"}
              onClick={() => {
                setOffset(0);
                setUnreadOnly(true);
              }}
              aria-pressed={unreadOnly}
            >
              غير المقروء ({unread})
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={unread === 0}
              onClick={() => void handleMarkAll()}
            >
              تعليم الكل كمقروء
            </Button>
          </div>

          <PageFeedback
            loading={loading}
            error={error}
            message={message}
            empty={
              !loading && items.length === 0
                ? {
                    title: "لا توجد إشعارات",
                    description: unreadOnly
                      ? "لا توجد إشعارات غير مقروءة."
                      : "ستظهر الإشعارات هنا عند توفرها.",
                  }
                : null
            }
            onRetry={() => void load()}
          >
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader
                dense
                title="قائمة الإشعارات"
                description={`عرض ${PAGE_SIZE} لكل صفحة — الإزاحة ${offset}`}
              />
              <ul className="space-y-3">
                {items.map((item) => (
                  <li
                    key={item.id}
                    className={cn(
                      "rounded-2xl border border-border/60 bg-surface px-5 py-4",
                      !item.is_read && "border-gold-primary/40",
                    )}
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div className="min-w-0 flex-1 space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="font-semibold text-black-primary">
                            {item.title}
                          </p>
                          {!item.is_read ? (
                            <Badge variant="outline">جديد</Badge>
                          ) : null}
                          <span className="text-xs text-muted">
                            {item.platform_event_kind}
                          </span>
                        </div>
                        <p className="text-sm text-muted">{item.body}</p>
                        <p className="text-xs text-muted">
                          {formatDate(item.materialized_at)}
                        </p>
                      </div>
                      {!item.is_read ? (
                        <Button
                          type="button"
                          size="sm"
                          variant="secondary"
                          onClick={() => void handleMarkRead(item.id)}
                        >
                          تعليم كمقروء
                        </Button>
                      ) : null}
                    </div>
                  </li>
                ))}
              </ul>
              <div className="flex flex-wrap gap-3">
                <Button
                  type="button"
                  variant="secondary"
                  disabled={offset === 0 || loading}
                  onClick={() => setOffset((value) => Math.max(0, value - PAGE_SIZE))}
                >
                  السابق
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  disabled={!hasMore || loading}
                  onClick={() => setOffset((value) => value + PAGE_SIZE)}
                >
                  التالي
                </Button>
              </div>
            </section>
          </PageFeedback>

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="تفضيلات الإشعارات"
              description="تفضيلات المستخدم الحالي — منفصلة عن إعدادات المنصة الافتراضية"
            />
            <div className="space-y-4 rounded-2xl border border-border/60 bg-surface px-5 py-5">
              <label className="flex items-center gap-3 text-sm">
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-[var(--gold-primary,#b8860b)]"
                  checked={prefsEnabled}
                  onChange={(event) => setPrefsEnabled(event.target.checked)}
                />
                تفعيل استلام الإشعارات
              </label>
              <label className="block space-y-1.5 text-sm">
                <span className="text-muted">
                  أنواع مكتومة (مفصولة بفاصلة)
                </span>
                <input
                  className="flex h-10 w-full rounded-lg border border-border bg-surface px-3 text-sm"
                  value={mutedKinds}
                  onChange={(event) => setMutedKinds(event.target.value)}
                />
              </label>
              <Button
                type="button"
                disabled={savingPrefs}
                onClick={() => void savePrefs()}
              >
                {savingPrefs ? "جاري الحفظ..." : "حفظ التفضيلات"}
              </Button>
              <p className="text-sm text-muted">
                لإعدادات المنصة الافتراضية راجع{" "}
                <Link href="/settings" className="text-gold-dark underline">
                  صفحة الإعدادات
                </Link>
                .
              </p>
            </div>
          </section>
        </div>
      </PageContainer>
    </AppLayout>
  );
}
