"use client";

import { cn } from "@/lib/utils";

export const NARRATIVE_UNAVAILABLE_AR =
  "الأرقام المعتمدة من المحرك معروضة؛ السرد التحليلي غير متاح حالياً";

export function NarrativeUnavailableNotice({
  narrativeStatus,
  className,
}: {
  narrativeStatus?: string | null;
  className?: string;
}) {
  if (!narrativeStatus) {
    return null;
  }
  return (
    <p
      role="status"
      className={cn(
        "rounded-xl border border-border/60 bg-surface px-4 py-3 text-sm leading-7 text-muted",
        className,
      )}
    >
      {NARRATIVE_UNAVAILABLE_AR}
    </p>
  );
}
