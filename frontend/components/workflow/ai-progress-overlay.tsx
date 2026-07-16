"use client";

import * as React from "react";
import { Sparkles } from "lucide-react";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { cn } from "@/lib/utils";

const AI_PROGRESS_STAGES = [
  "إعداد السياق المالي",
  "تحليل الأنماط المالية",
  "توليد التوصيات التنفيذية",
  "تهيئة التوصيات للعرض",
  "على وشك الاكتمال",
] as const;

/** Advance informational stage every 35s — not a completion percentage. */
const STAGE_INTERVAL_MS = 35_000;

function useAiProgressStage(active: boolean): number {
  const [stageIndex, setStageIndex] = React.useState(0);

  React.useEffect(() => {
    if (!active) {
      setStageIndex(0);
      return;
    }

    const startedAt = Date.now();
    const tick = () => {
      const elapsed = Date.now() - startedAt;
      const nextIndex = Math.min(
        Math.floor(elapsed / STAGE_INTERVAL_MS),
        AI_PROGRESS_STAGES.length - 1,
      );
      setStageIndex(nextIndex);
    };

    tick();
    const interval = window.setInterval(tick, 2_000);
    return () => window.clearInterval(interval);
  }, [active]);

  return stageIndex;
}

export interface AiProgressOverlayProps {
  open: boolean;
}

export function AiProgressOverlay({ open }: AiProgressOverlayProps) {
  const stageIndex = useAiProgressStage(open);

  if (!open) {
    return null;
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="ai-progress-title"
      aria-describedby="ai-progress-description"
      className="fixed inset-0 z-[60] flex items-center justify-center bg-black-primary/45 px-4 backdrop-blur-[2px]"
    >
      <div className="w-full max-w-md rounded-2xl border border-border bg-surface p-6 shadow-elevated">
        <div className="flex items-start gap-4">
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gold-primary/10 text-gold-dark">
            <Sparkles className="h-6 w-6" strokeWidth={1.75} />
          </span>
          <div className="min-w-0 flex-1 space-y-2">
            <h2
              id="ai-progress-title"
              className="text-lg font-semibold text-black-primary"
            >
              جاري توليد التوصيات التنفيذية
            </h2>
            <p id="ai-progress-description" className="text-sm leading-relaxed text-muted">
              قد تستغرق العملية من دقيقة إلى ثلاث دقائق حسب حجم البيانات. يرجى
              الانتظار دون إغلاق الصفحة.
            </p>
          </div>
        </div>

        <div className="mt-6 space-y-4">
          <div className="flex items-center gap-3">
            <LoadingSpinner size="md" label="جاري توليد التوصيات" />
            <p className="text-sm font-medium text-black-primary">
              {AI_PROGRESS_STAGES[stageIndex]}
            </p>
          </div>

          <ul className="space-y-2">
            {AI_PROGRESS_STAGES.map((stage, index) => (
              <li
                key={stage}
                className={cn(
                  "flex items-center gap-2 text-sm transition-colors",
                  index < stageIndex
                    ? "text-gray-medium"
                    : index === stageIndex
                      ? "font-semibold text-gold-dark"
                      : "text-muted",
                )}
              >
                <span
                  className={cn(
                    "h-1.5 w-1.5 shrink-0 rounded-full",
                    index <= stageIndex ? "bg-gold-primary" : "bg-border",
                  )}
                />
                {stage}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
