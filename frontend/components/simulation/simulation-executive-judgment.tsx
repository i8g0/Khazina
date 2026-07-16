"use client";

import { Badge } from "@/components/ui/badge";
import type { ExecutiveJudgmentPayload } from "@/lib/api/types";
import { ensureExecutiveArabic } from "@/lib/executive-language";
import { cn } from "@/lib/utils";

export interface SimulationExecutiveJudgmentProps {
  judgment: ExecutiveJudgmentPayload;
  className?: string;
}

function recommendationVariant(rec: string) {
  if (rec === "الرفض") return "destructive" as const;
  if (rec === "التأجيل") return "secondary" as const;
  if (rec === "الموافقة مع تعديلات") return "warning" as const;
  return "default" as const;
}

export function SimulationExecutiveJudgment({
  judgment,
  className,
}: SimulationExecutiveJudgmentProps) {
  return (
    <article
      className={cn(
        "rounded-2xl border border-gold-primary/25 bg-gradient-to-b from-gold-primary/5 to-surface px-5 py-6 md:px-7",
        className,
      )}
    >
      <header className="mb-5 flex flex-wrap items-center gap-3">
        <h3 className="text-lg font-semibold text-black-primary md:text-xl">
          الحكم التنفيذي
        </h3>
        <Badge variant={recommendationVariant(judgment.recommendation)}>
          {judgment.recommendation}
        </Badge>
      </header>

      <p className="mb-5 text-sm font-medium leading-relaxed text-black-primary">
        {ensureExecutiveArabic(judgment.executive_verdict)}
      </p>

      <div className="grid gap-4 md:grid-cols-2">
        <JudgmentBlock title="تحليل الأهمية النسبية" body={judgment.materiality_analysis} />
        <JudgmentBlock title="واقعية التنفيذ المالي" body={judgment.financial_realism} />
        <JudgmentBlock title="مقارنة مقياس المنشأة" body={judgment.scale_comparison} />
        <JudgmentBlock title="النصيحة الاستراتيجية" body={judgment.strategic_advice} />
        <JudgmentBlock title="التبرير المالي" body={judgment.financial_reasoning} emphasis />
        <JudgmentBlock title="المبرر" body={judgment.recommendation_rationale} />
      </div>

      <section className="mt-5 border-t border-border/50 pt-5">
        <h4 className="mb-3 text-sm font-semibold text-muted">الحكم النهائي للمجلس</h4>
        <dl className="grid gap-3 text-sm md:grid-cols-2">
          <VerdictRow label="التبرير المالي" value={judgment.financial_justification} />
          <VerdictRow label="التوصية الاستراتيجية" value={judgment.strategic_recommendation} />
          <VerdictRow label="الثقة" value={judgment.confidence_statement} />
          <VerdictRow label="البديل المقترح" value={judgment.alternative_option} />
          <VerdictRow label="الخطوة التالية" value={judgment.next_step} />
        </dl>
      </section>

      {judgment.supporting_indicators.length > 0 ? (
        <section className="mt-4">
          <p className="mb-2 text-xs font-semibold text-muted">المؤشرات الداعمة</p>
          <ul className="list-inside list-disc space-y-1 text-sm text-black-primary/90">
            {judgment.supporting_indicators.map((item) => (
              <li key={item}>{ensureExecutiveArabic(item)}</li>
            ))}
          </ul>
        </section>
      ) : null}

      {judgment.assumptions_used.length > 0 ? (
        <section className="mt-4">
          <p className="mb-2 text-xs font-semibold text-muted">الافتراضات</p>
          <ul className="list-inside list-disc space-y-1 text-sm text-muted">
            {judgment.assumptions_used.map((item) => (
              <li key={item}>{ensureExecutiveArabic(item)}</li>
            ))}
          </ul>
        </section>
      ) : null}

      <p className="mt-4 text-sm text-muted">
        <span className="font-semibold text-black-primary/80">المخاطر المتبقية: </span>
        {ensureExecutiveArabic(judgment.remaining_risks)}
      </p>
    </article>
  );
}

function JudgmentBlock({
  title,
  body,
  emphasis,
}: {
  title: string;
  body: string;
  emphasis?: boolean;
}) {
  return (
    <div className="rounded-xl border border-border/40 bg-surface/60 p-4">
      <p className="mb-2 text-xs font-semibold text-muted">{title}</p>
      <p
        className={cn(
          "text-sm leading-relaxed",
          emphasis ? "font-medium text-black-primary" : "text-black-primary/90",
        )}
      >
        {ensureExecutiveArabic(body)}
      </p>
    </div>
  );
}

function VerdictRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="mt-0.5 text-sm leading-relaxed text-black-primary/90">
        {ensureExecutiveArabic(value)}
      </dd>
    </div>
  );
}
