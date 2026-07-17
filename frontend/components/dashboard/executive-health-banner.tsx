import { Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ExecutiveHealthLevel } from "@/lib/dashboard/command-center-types";

const levelStyles: Record<
  ExecutiveHealthLevel,
  { bar: string; badge: string; ring: string }
> = {
  excellent: {
    bar: "bg-emerald-500",
    badge: "bg-emerald-500/10 text-emerald-700",
    ring: "border-emerald-500/30",
  },
  good: {
    bar: "bg-gold-primary",
    badge: "bg-gold-primary/10 text-gold-dark",
    ring: "border-gold-primary/30",
  },
  needs_attention: {
    bar: "bg-amber-500",
    badge: "bg-amber-500/10 text-amber-700",
    ring: "border-amber-500/30",
  },
  critical: {
    bar: "bg-red-600",
    badge: "bg-red-600/10 text-red-700",
    ring: "border-red-600/30",
  },
};

export interface ExecutiveHealthBannerProps {
  score: number;
  level: ExecutiveHealthLevel;
  labelAr: string;
}

export function ExecutiveHealthBanner({
  score,
  level,
  labelAr,
}: ExecutiveHealthBannerProps) {
  const styles = levelStyles[level];

  return (
    <section
      className={cn(
        "rounded-2xl border bg-surface px-5 py-4 md:px-6 md:py-5",
        styles.ring,
      )}
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-bg-light text-gold-dark">
            <Activity className="h-5 w-5" strokeWidth={1.75} />
          </span>
          <div>
            <p className="text-sm font-medium text-muted">مؤشر الصحة المالية التنفيذي</p>
            <p className="text-xl font-semibold tracking-tight text-black-primary">
              {labelAr}
            </p>
          </div>
        </div>
        <span
          className={cn(
            "rounded-full px-3 py-1 text-sm font-semibold tabular-nums",
            styles.badge,
          )}
        >
          {score}/100
        </span>
      </div>
      <div className="mt-4 h-2 overflow-hidden rounded-full bg-bg-light">
        <div
          className={cn("h-full rounded-full transition-all", styles.bar)}
          style={{ width: `${score}%` }}
        />
      </div>
    </section>
  );
}
