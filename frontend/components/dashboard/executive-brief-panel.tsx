import { Sparkles } from "lucide-react";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { NarrativeUnavailableNotice } from "@/lib/narrative-status";

export interface ExecutiveBriefPanelProps {
  brief: string | null;
  briefParts: { domain: string; text: string }[];
  boardRecommendation: string | null;
  narrativeStatus: string | null;
}

export function ExecutiveBriefPanel({
  brief,
  briefParts,
  boardRecommendation,
  narrativeStatus,
}: ExecutiveBriefPanelProps) {
  return (
    <section className="rounded-2xl border border-gold-primary/20 bg-gradient-to-br from-surface via-surface to-gold-primary/5 px-5 py-5 md:px-6 md:py-6">
      <div className="mb-4 flex items-start gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gold-primary/10 text-gold-dark">
          <Sparkles className="h-5 w-5" strokeWidth={1.75} />
        </span>
        <DashboardSectionHeader
          dense
          title="الملخص التنفيذي"
          description="قصة البيانات المالية — من الهدر والمخاطر إلى القرار"
        />
      </div>

      {brief ? (
        <p className="text-[15px] leading-8 text-black-primary md:text-base">
          {brief}
        </p>
      ) : (
        <p className="text-sm leading-7 text-muted">
          ارفع البيانات ونفّذ تحليل الهدر والمخاطر لإنشاء ملخص تنفيذي موحّد.
        </p>
      )}

      {briefParts.length > 1 ? (
        <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {briefParts.map((part) => (
            <div
              key={part.domain}
              className="rounded-xl border border-border/60 bg-surface/80 px-4 py-3"
            >
              <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gold-dark">
                {part.domain}
              </p>
              <p className="text-sm leading-6 text-muted">{part.text}</p>
            </div>
          ))}
        </div>
      ) : null}

      {boardRecommendation ? (
        <div className="mt-5 rounded-xl border border-border/60 bg-bg-light/50 px-4 py-3">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gold-dark">
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
