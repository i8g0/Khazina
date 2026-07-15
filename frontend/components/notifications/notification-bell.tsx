"use client";

import * as React from "react";
import Link from "next/link";
import { Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Modal,
  ModalContent,
  ModalDescription,
  ModalHeader,
  ModalTitle,
} from "@/components/ui/modal";
import { useAuth, formatApiError } from "@/lib/auth/auth-context";
import {
  getUnreadCount,
  listNotifications,
  markNotificationRead,
} from "@/lib/api/khazina-api";
import type { NotificationResponse } from "@/lib/api/types";

export function NotificationBell() {
  const { session } = useAuth();
  const [open, setOpen] = React.useState(false);
  const [unread, setUnread] = React.useState(0);
  const [items, setItems] = React.useState<NotificationResponse[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const refreshCount = React.useCallback(async () => {
    if (!session) return;
    try {
      const count = await getUnreadCount(session.organizationId, session.token);
      setUnread(count);
    } catch {
      /* keep last known count on poll failure */
    }
  }, [session]);

  const refreshList = React.useCallback(async () => {
    if (!session) return;
    setLoading(true);
    setError(null);
    try {
      const [count, notifications] = await Promise.all([
        getUnreadCount(session.organizationId, session.token),
        listNotifications(session.organizationId, session.token, {
          limit: 8,
          offset: 0,
        }),
      ]);
      setUnread(count);
      setItems(notifications);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [session]);

  React.useEffect(() => {
    void refreshCount();
    const timer = window.setInterval(() => void refreshCount(), 30_000);
    return () => window.clearInterval(timer);
  }, [refreshCount]);

  const handleOpen = (next: boolean) => {
    setOpen(next);
    if (next) void refreshList();
  };

  const handleMarkRead = async (id: string) => {
    if (!session) return;
    await markNotificationRead(session.organizationId, session.token, id);
    await refreshList();
  };

  return (
    <>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="relative"
        onClick={() => handleOpen(true)}
        aria-label={`الإشعارات${unread > 0 ? ` — ${unread} غير مقروء` : ""}`}
      >
        <Bell className="h-5 w-5" aria-hidden />
        {unread > 0 ? (
          <span className="absolute -left-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-gold px-1 text-[11px] font-semibold text-white">
            {unread > 9 ? "9+" : unread}
          </span>
        ) : null}
      </Button>

      <Modal open={open} onOpenChange={handleOpen}>
        <ModalContent>
          <ModalHeader>
            <ModalTitle>الإشعارات</ModalTitle>
            <ModalDescription>أحدث إشعارات المنصة</ModalDescription>
          </ModalHeader>
          {loading ? (
            <p className="text-sm text-muted" role="status">
              جاري التحميل...
            </p>
          ) : error ? (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : items.length === 0 ? (
            <p className="text-sm text-muted">لا توجد إشعارات حالياً</p>
          ) : (
            <ul className="max-h-[360px] space-y-3 overflow-y-auto">
              {items.map((item) => (
                <li
                  key={item.id}
                  className="rounded-xl border border-border/70 bg-surface p-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-foreground">
                        {item.title}
                      </p>
                      <p className="mt-1 text-xs text-muted">{item.body}</p>
                    </div>
                    {!item.is_read ? (
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => void handleMarkRead(item.id)}
                      >
                        مقروء
                      </Button>
                    ) : null}
                  </div>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-4">
            <Button asChild variant="secondary" size="sm">
              <Link href="/notifications" onClick={() => setOpen(false)}>
                فتح مركز الإشعارات
              </Link>
            </Button>
          </div>
        </ModalContent>
      </Modal>
    </>
  );
}

export function DemoHeaderActions() {
  const { signOut } = useAuth();
  return (
    <div className="flex items-center gap-2">
      <NotificationBell />
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={signOut}
        aria-label="تسجيل الخروج"
      >
        خروج
      </Button>
    </div>
  );
}
