import Link from "next/link";
import {
  ArrowDown,
  CheckCircle2,
  FileUp,
  LineChart,
  PiggyBank,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { EmptyState } from "@/components/ui/empty-state";
import type { StoryTimelineStep } from "@/lib/dashboard/command-center-types";

const stepIcons: Record<string, typeof FileUp> = {
  upload: FileUp,
  waste: PiggyBank,
  risk: ShieldAlert,
  simulation: LineChart,
  savings: Sparkles,
  board: CheckCircle2,
  reports: CheckCircle2,
};

export interface ExecutiveStoryTimelineProps {
  steps: StoryTimelineStep[];
}

export function ExecutiveStoryTimeline({ steps }: ExecutiveStoryTimelineProps) {
  return (
    <section className="space-y-4">
      <DashboardSectionHeader
        dense
        title="الخط الزمني التنفيذي"
        description="قصة البيانات من الرفع إلى توصية مجلس الإدارة"
      />
      {steps.length === 0 ? (
        <EmptyState
          title="القصة لم تبدأ بعد"
          description="ارفع البيانات المالية لبدء سرد القرار التنفيذي"
        />
      ) : (
        <div className="rounded-2xl border border-border/60 bg-surface px-4 py-5 md:px-6 md:py-6">
          <ol className="space-y-0">
            {steps.map((step, index) => {
              const Icon = stepIcons[step.id] ?? Sparkles;
              const isLast = index === steps.length - 1;
              const content = (
                <>
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-gold-primary/25 bg-gold-primary/10 text-gold-dark">
                    <Icon className="h-[18px] w-[18px]" strokeWidth={1.75} />
                  </span>
                  <div className="min-w-0 flex-1 pt-1">
                    <p className="text-[15px] font-semibold leading-snug text-black-primary md:text-base">
                      {step.title}
                    </p>
                    {step.detail ? (
                      <p className="mt-1 text-sm leading-6 text-muted">{step.detail}</p>
                    ) : null}
                  </div>
                </>
              );

              return (
                <li key={step.id}>
                  {step.href ? (
                    <Link
                      href={step.href}
                      className="group flex gap-4 rounded-xl px-1 py-2 transition-colors hover:bg-bg-light/60"
                    >
                      {content}
                    </Link>
                  ) : (
                    <div className="flex gap-4 px-1 py-2">{content}</div>
                  )}
                  {!isLast ? (
                    <div className="flex justify-center py-1" aria-hidden="true">
                      <ArrowDown className="h-4 w-4 text-gold-primary/50" />
                    </div>
                  ) : null}
                </li>
              );
            })}
          </ol>
        </div>
      )}
    </section>
  );
}
