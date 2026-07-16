"use client";

import Link from "next/link";
import { Database, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { navRouteMap } from "@/lib/app-nav";

export interface RiskIdleContentProps {
  hasUploadedFile: boolean;
  onRunAnalysis: () => void;
  className?: string;
}

export function RiskIdleContent({
  hasUploadedFile,
  onRunAnalysis,
  className,
}: RiskIdleContentProps) {
  return (
    <div className={cn("space-y-5 md:space-y-6", className)}>
      <section className="rounded-2xl border border-border/60 bg-surface px-5 py-5 md:px-7 md:py-6">
        <p className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-muted">
          كيف يعمل
        </p>
        <ol className="grid gap-4 sm:grid-cols-3">
          {[
            { label: "رفع البيانات المالية", icon: Database },
            { label: "تشغيل تحليل المخاطر", icon: ShieldAlert },
            { label: "مراجعة النتائج والترقية", icon: ShieldAlert },
          ].map((step) => {
            const Icon = step.icon;
            return (
              <li
                key={step.label}
                className="flex items-start gap-3 rounded-xl border border-border/50 bg-bg-light/40 px-4 py-3"
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gold-primary/10 text-gold-dark">
                  <Icon className="h-4 w-4" strokeWidth={1.75} />
                </span>
                <span className="pt-1 text-sm font-medium text-gray-medium">
                  {step.label}
                </span>
              </li>
            );
          })}
        </ol>
      </section>

      {hasUploadedFile ? (
        <div className="flex flex-wrap gap-3">
          <Button onClick={onRunAnalysis}>تشغيل تحليل المخاطر</Button>
        </div>
      ) : (
        <div className="flex flex-wrap gap-3">
          <Button asChild>
            <Link href={navRouteMap.data}>الانتقال إلى مركز البيانات المالية</Link>
          </Button>
        </div>
      )}
    </div>
  );
}
