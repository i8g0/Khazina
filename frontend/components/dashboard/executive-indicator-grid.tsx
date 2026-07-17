import Link from "next/link";
import {
  AlertTriangle,
  BrainCircuit,
  Building2,
  ClipboardCheck,
  LineChart,
  PiggyBank,
  ShieldAlert,
  Truck,
} from "lucide-react";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import type { ExecutiveIndicator } from "@/lib/dashboard/command-center-types";
import { cn } from "@/lib/utils";

const indicatorIcons: Record<string, typeof ShieldAlert> = {
  "money-at-risk": ShieldAlert,
  "recoverable-savings": PiggyBank,
  "top-risk-dept": Building2,
  "top-waste-vendor": Truck,
  "urgent-decisions": ClipboardCheck,
  "simulation-readiness": LineChart,
  "ai-confidence": BrainCircuit,
  "board-attention": AlertTriangle,
};

export interface ExecutiveIndicatorGridProps {
  indicators: ExecutiveIndicator[];
}

export function ExecutiveIndicatorGrid({ indicators }: ExecutiveIndicatorGridProps) {
  return (
    <section className="space-y-4">
      <DashboardSectionHeader
        dense
        title="مؤشرات القرار التنفيذي"
        description="أرقام تجيب: أين الخطر؟ أين الهدر؟ ماذا أفعل الآن؟"
      />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {indicators.map((indicator) => {
          const Icon = indicatorIcons[indicator.id] ?? ShieldAlert;
          const hasValue = Boolean(indicator.value);

          return (
            <Link
              key={indicator.id}
              href={indicator.href}
              className={cn(
                "group flex min-h-[120px] flex-col rounded-2xl border border-border/60 bg-surface px-4 py-4 transition-colors hover:border-gold-primary/30 md:px-5 md:py-5",
              )}
            >
              <div className="mb-3 flex items-start justify-between gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-bg-light text-gold-primary/80">
                  <Icon className="h-[17px] w-[17px]" strokeWidth={1.75} />
                </span>
                <span className="text-[11px] font-medium text-muted opacity-0 transition-opacity group-hover:opacity-100">
                  عرض التفاصيل
                </span>
              </div>
              {hasValue ? (
                <p className="text-xl font-semibold leading-tight tracking-tight text-black-primary md:text-2xl">
                  {indicator.value}
                </p>
              ) : (
                <p className="text-sm leading-relaxed text-muted">
                  {indicator.emptyMessage}
                </p>
              )}
              <p className="mt-2 text-xs font-medium text-muted">{indicator.label}</p>
              {indicator.hint ? (
                <p className="mt-1 text-[11px] text-gold-dark/80">{indicator.hint}</p>
              ) : null}
            </Link>
          );
        })}
      </div>
    </section>
  );
}
