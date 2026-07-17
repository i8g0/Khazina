import { Sparkles } from "lucide-react";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import type {
  ExecutiveBriefFact,
  ExecutiveBriefSection,
} from "@/lib/dashboard/command-center-types";
import { NarrativeUnavailableNotice } from "@/lib/narrative-status";
import { cn } from "@/lib/utils";

export interface ExecutiveBriefPanelProps {
  brief: string | null;
  briefParts: { domain: string; text: string }[];
  briefFacts: ExecutiveBriefFact[];
  briefSections: ExecutiveBriefSection[];
  boardRecommendation: string | null;
  narrativeStatus: string | null;
}

const TONE_VALUE: Record<NonNullable<ExecutiveBriefFact["tone"]>, string> = {
  neutral: "text-black-primary",
  attention: "text-amber-800",
  positive: "text-emerald-800",
  critical: "text-red-800",
};

export function ExecutiveBriefPanel({
  brief,
  briefParts,
  briefFacts,
  briefSections,
  boardRecommendation,
  narrativeStatus,
}: ExecutiveBriefPanelProps) {
  const hasContent =
    briefFacts.length > 0 ||
    briefSections.length > 0 ||
    Boolean(brief) ||
    Boolean(boardRecommendation);

  return (
    <section className="rounded-2xl border border-gold-primary/20 bg-gradient-to-br from-surface via-surface to-gold-primary/5 px-5 py-5 md:px-6 md:py-6">
      <div className="mb-5 flex items-start gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gold-primary/10 text-gold-dark">
          <Sparkles className="h-5 w-5" strokeWidth={1.75} />
        </span>
        <DashboardSectionHeader
          dense
          title="الملخص التنفيذي"
          description="أرقام أولاً، ثم التفسير — جاهز لمراجعة المدير المالي"
        />
      </div>

      {!hasContent ? (
        <p className="text-sm leading-7 text-muted">
          ارفع البيانات ونفّذ تحليل الهدر والمخاطر لإنشاء ملخص تنفيذي موحّد.
        </p>
      ) : null}

      {briefFacts.length > 0 ? (
        <div className="mb-5">
          <p className="mb-3 text-xs font-semibold tracking-wide text-gold-dark">
            المؤشرات المالية الأساسية
          </p>
          <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {briefFacts.map((fact) => (
              <div
                key={fact.id}
                className="rounded-xl border border-border/50 bg-surface/90 px-4 py-3"
              >
                <dt className="text-xs font-medium text-muted">{fact.label}</dt>
                <dd
                  className={cn(
                    "mt-1 text-lg font-semibold tracking-tight md:text-xl",
                    TONE_VALUE[fact.tone ?? "neutral"],
                  )}
                >
                  {fact.value}
                </dd>
                {fact.hint ? (
                  <p className="mt-1 text-[12px] leading-5 text-muted">{fact.hint}</p>
                ) : null}
              </div>
            ))}
          </dl>
        </div>
      ) : null}

      {briefSections.length > 0 ? (
        <div className="mb-5">
          <p className="mb-3 text-xs font-semibold tracking-wide text-gold-dark">
            قراءة التحليل
          </p>
          <dl className="divide-y divide-border/40 overflow-hidden rounded-xl border border-border/50 bg-surface/70">
            {briefSections.map((section) => (
              <div
                key={section.id}
                className="grid gap-1 px-4 py-3.5 sm:grid-cols-[9.5rem_1fr] sm:gap-4"
              >
                <dt className="text-sm font-semibold text-black-primary">
                  {section.label}
                </dt>
                <dd className="text-sm leading-7 text-black-primary/90">
                  {section.body}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      ) : brief ? (
        <p className="mb-5 text-[15px] leading-8 text-black-primary md:text-base">
          {brief}
        </p>
      ) : null}

      {briefParts.length > 0 ? (
        <div className="mb-5 flex flex-wrap gap-2">
          {briefParts.map((part) => (
            <span
              key={part.domain}
              className="rounded-md border border-border/50 bg-bg-light/60 px-2.5 py-1 text-[11px] font-medium text-muted"
            >
              مصدر: {part.domain}
            </span>
          ))}
        </div>
      ) : null}

      {boardRecommendation ? (
        <div className="rounded-xl border border-gold-primary/25 bg-gold-primary/5 px-4 py-4">
          <p className="mb-2 text-xs font-semibold tracking-wide text-gold-dark">
            توصية مجلس الإدارة
          </p>
          <p className="text-sm leading-7 text-black-primary">{boardRecommendation}</p>
        </div>
      ) : null}

      <NarrativeUnavailableNotice
        narrativeStatus={narrativeStatus}
        className="mt-4"
      />
    </section>
  );
}
