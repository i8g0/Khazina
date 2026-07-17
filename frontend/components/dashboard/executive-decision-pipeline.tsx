import Link from "next/link";
import { CheckCircle2, Circle } from "lucide-react";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import type { DecisionPipelineStep } from "@/lib/dashboard/command-center-types";
import { cn } from "@/lib/utils";

export interface ExecutiveDecisionPipelineProps {
  steps: DecisionPipelineStep[];
}

export function ExecutiveDecisionPipeline({ steps }: ExecutiveDecisionPipelineProps) {
  return (
    <section className="space-y-4">
      <DashboardSectionHeader
        dense
        title="حالة دورة القرار"
        description="ما اكتمل وما يتطلب إجراءً تنفيذياً"
      />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {steps.map((step) => (
          <Link
            key={step.id}
            href={step.href}
            className={cn(
              "group flex flex-col rounded-2xl border border-border/60 bg-surface px-4 py-4 transition-colors hover:border-gold-primary/30",
              !step.completed && "opacity-90",
            )}
          >
            <div className="mb-2 flex items-center justify-between gap-2">
              {step.completed ? (
                <CheckCircle2
                  className="h-5 w-5 shrink-0 text-emerald-600"
                  strokeWidth={1.75}
                />
              ) : (
                <Circle
                  className="h-5 w-5 shrink-0 text-muted"
                  strokeWidth={1.75}
                />
              )}
              <span className="text-[11px] font-medium text-muted group-hover:text-gold-dark">
                {step.completed ? "مكتمل" : "معلق"}
              </span>
            </div>
            <p className="text-sm font-semibold text-black-primary">{step.label}</p>
            {step.detail ? (
              <p className="mt-1 text-xs text-muted">{step.detail}</p>
            ) : null}
          </Link>
        ))}
      </div>
    </section>
  );
}
