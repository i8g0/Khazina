"use client";

import * as React from "react";
import { Activity } from "lucide-react";
import { getAiHealth, getSystemHealth } from "@/lib/api/khazina-api";
import { cn } from "@/lib/utils";

interface StatusChipProps {
  label: string;
  status: string;
  message?: string;
}

function StatusChip({ label, status, message }: StatusChipProps) {
  const ok = status === "ok";
  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-xl border px-3 py-2 text-sm",
        ok
          ? "border-emerald-200 bg-emerald-50 text-emerald-900"
          : "border-amber-200 bg-amber-50 text-amber-950",
      )}
      title={message}
    >
      <span
        className={cn(
          "h-2 w-2 rounded-full",
          ok ? "bg-emerald-500" : "bg-amber-500",
        )}
      />
      <span className="font-medium">{label}</span>
      <span className="text-xs opacity-80">{ok ? "متاح" : "غير متاح"}</span>
    </div>
  );
}

export function SystemStatusBanner({ className }: { className?: string }) {
  const [backendStatus, setBackendStatus] = React.useState("ok");
  const [databaseStatus, setDatabaseStatus] = React.useState("ok");
  const [aiStatus, setAiStatus] = React.useState("ok");
  const [databaseMessage, setDatabaseMessage] = React.useState<string>();
  const [aiMessage, setAiMessage] = React.useState<string>();

  React.useEffect(() => {
    void (async () => {
      try {
        const health = await getSystemHealth();
        setBackendStatus(health.backend?.status ?? health.status);
        setDatabaseStatus(health.database?.status ?? "ok");
        setDatabaseMessage(health.database?.message);
        const ai = await getAiHealth();
        setAiStatus(ai.status);
        setAiMessage(ai.message);
      } catch {
        setBackendStatus("unavailable");
      }
    })();
  }, []);

  const allOk =
    backendStatus === "ok" && databaseStatus === "ok" && aiStatus === "ok";

  return (
    <section
      className={cn(
        "rounded-2xl border border-border/60 bg-surface px-4 py-3 md:px-5",
        className,
      )}
      aria-label="حالة النظام"
    >
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-2 text-sm font-medium text-black-primary">
          <Activity className="h-4 w-4 text-gold-primary" />
          {allOk ? "جميع خدمات التحليل متاحة" : "بعض خدمات التحليل غير متاحة حالياً"}
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusChip label="الخادم" status={backendStatus} />
          <StatusChip
            label="قاعدة البيانات"
            status={databaseStatus}
            message={databaseMessage}
          />
          <StatusChip label="الذكاء الاصطناعي" status={aiStatus} message={aiMessage} />
        </div>
      </div>
    </section>
  );
}
