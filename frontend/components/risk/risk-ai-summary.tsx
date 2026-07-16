"use client";

import { Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

export interface RiskAiSummaryProps {
  executiveSummary?: string | null;
  executiveBrief?: string | null;
  explanation?: string | null;
  boardReport?: string | null;
  className?: string;
}

export function RiskAiSummary({
  executiveSummary,
  executiveBrief,
  explanation,
  boardReport,
  className,
}: RiskAiSummaryProps) {
  const sections = [
    { title: "الملخص التنفيذي", body: executiveSummary },
    { title: "الموجز التنفيذي", body: executiveBrief },
    { title: "شرح المخاطر", body: explanation },
    { title: "تقرير مجلس الإدارة", body: boardReport },
  ].filter((section) => Boolean(section.body?.trim()));

  if (sections.length === 0) {
    return null;
  }

  return (
    <article
      className={cn(
        "rounded-2xl border border-border/60 bg-surface px-5 py-5 md:px-6 md:py-6",
        className,
      )}
    >
      <div className="mb-5 flex items-center gap-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gold-primary/10 text-gold-dark">
          <Sparkles className="h-[18px] w-[18px]" strokeWidth={1.75} />
        </span>
        <div>
          <h3 className="text-lg font-semibold text-black-primary">ملخص الذكاء الاصطناعي</h3>
          <p className="text-xs text-muted">شرح وتوصيات — المصدر الحتمي للدرجات هو محرك المخاطر</p>
        </div>
      </div>
      <div className="space-y-5">
        {sections.map((section) => (
          <div key={section.title} className="space-y-2">
            <h4 className="text-sm font-semibold text-gray-medium">{section.title}</h4>
            <p className="whitespace-pre-wrap text-sm leading-7 text-muted md:text-[15px]">
              {section.body}
            </p>
          </div>
        ))}
      </div>
    </article>
  );
}
