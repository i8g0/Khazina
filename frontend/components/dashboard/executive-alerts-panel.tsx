import Link from "next/link";
import { AlertTriangle, ArrowLeft, Info } from "lucide-react";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { EmptyState } from "@/components/ui/empty-state";
import type { ExecutiveAlert } from "@/lib/dashboard/command-center-types";
import { cn } from "@/lib/utils";

const severityStyles: Record<
  ExecutiveAlert["severity"],
  { icon: typeof AlertTriangle; border: string; iconColor: string }
> = {
  critical: {
    icon: AlertTriangle,
    border: "border-red-500/25 hover:border-red-500/40",
    iconColor: "text-red-600 bg-red-500/10",
  },
  warning: {
    icon: AlertTriangle,
    border: "border-amber-500/25 hover:border-amber-500/40",
    iconColor: "text-amber-600 bg-amber-500/10",
  },
  info: {
    icon: Info,
    border: "border-gold-primary/25 hover:border-gold-primary/40",
    iconColor: "text-gold-dark bg-gold-primary/10",
  },
};

export interface ExecutiveAlertsPanelProps {
  alerts: ExecutiveAlert[];
}

export function ExecutiveAlertsPanel({ alerts }: ExecutiveAlertsPanelProps) {
  return (
    <section className="space-y-4">
      <DashboardSectionHeader
        dense
        title="تنبيهات تنفيذية"
        description="إجراءات تتطلب انتباهك الآن"
      />
      {alerts.length === 0 ? (
        <EmptyState
          title="لا تنبيهات عاجلة"
          description="ستظهر هنا المخاطر والهدر والقرارات التي تتطلب تدخلاً"
        />
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {alerts.map((alert) => {
            const styles = severityStyles[alert.severity];
            const Icon = styles.icon;
            return (
              <Link
                key={alert.id}
                href={alert.href}
                className={cn(
                  "group flex items-start gap-3 rounded-2xl border bg-surface px-4 py-4 transition-colors",
                  styles.border,
                )}
              >
                <span
                  className={cn(
                    "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg",
                    styles.iconColor,
                  )}
                >
                  <Icon className="h-[18px] w-[18px]" strokeWidth={1.75} />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-black-primary">{alert.title}</p>
                  <p className="mt-1 text-sm leading-6 text-muted">
                    {alert.description}
                  </p>
                </div>
                <ArrowLeft
                  className="mt-1 h-4 w-4 shrink-0 text-muted opacity-0 transition-opacity group-hover:opacity-100"
                  strokeWidth={1.75}
                />
              </Link>
            );
          })}
        </div>
      )}
    </section>
  );
}
