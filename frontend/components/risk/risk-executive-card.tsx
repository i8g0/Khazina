"use client";

import { Badge } from "@/components/ui/badge";
import type { RiskExecutiveCardView } from "@/lib/risk/view-types";
import { cn } from "@/lib/utils";

export interface RiskExecutiveCardProps {
  item: RiskExecutiveCardView;
  className?: string;
  onSelect?: (id: string) => void;
  selected?: boolean;
}

function priorityVariant(priority: string) {
  if (priority === "عالية") return "warning" as const;
  if (priority === "متوسطة") return "secondary" as const;
  return "default" as const;
}

export function RiskExecutiveCard({
  item,
  className,
  onSelect,
  selected,
}: RiskExecutiveCardProps) {
  return (
    <article
      role={onSelect ? "button" : undefined}
      tabIndex={onSelect ? 0 : undefined}
      onClick={() => onSelect?.(item.id)}
      onKeyDown={(e) => {
        if (onSelect && (e.key === "Enter" || e.key === " ")) {
          e.preventDefault();
          onSelect(item.id);
        }
      }}
      className={cn(
        "flex flex-col rounded-2xl border bg-surface px-5 py-5 transition-colors md:px-6",
        selected ? "border-gold-primary/50 ring-1 ring-gold-primary/20" : "border-border/60",
        onSelect && "cursor-pointer hover:border-gold-primary/30",
        className,
      )}
    >
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <Badge variant={priorityVariant(item.priority)}>{item.priority}</Badge>
        <span className="text-xs text-muted">درجة {item.score}/100</span>
        {item.confidence !== "—" ? (
          <span className="text-xs text-muted">ثقة {item.confidence}</span>
        ) : null}
      </div>

      <h3 className="mb-2 text-lg font-semibold leading-snug text-black-primary">
        {item.title}
      </h3>

      <Block title="الملخص التنفيذي" body={item.executiveSummary} />

      <dl className="mt-3 grid gap-2 text-sm">
        <Row label="سبب الاكتشاف" value={item.detectionReason} />
        <Row label="الإدارة" value={item.department} />
        <Row label="المورد" value={item.supplier} />
        {item.supplierCount !== "—" ? (
          <Row label="عدد الموردين" value={item.supplierCount} />
        ) : null}
        <Row label="الفئة المتأثرة" value={item.affectedCategory} />
        <Row label="المبلغ المعرّض" value={item.amountExposed} emphasis />
        <Row label="قيمة الهدر" value={item.wasteValue} emphasis />
        <Row label="الأثر المالي" value={item.financialImpact} />
        <Row label="احتمالية الحدوث" value={item.probability} />
        <Row label="الأثر التجاري" value={item.businessImpact} />
        <Row label="الوفورات المتوقعة" value={item.estimatedSavings} emphasis />
        <Row label="المسؤول" value={item.targetOwner} />
        <Row label="المدة" value={item.targetTimeline} />
      </dl>

      <div className="mt-4 space-y-3 border-t border-border/50 pt-4 text-sm leading-relaxed">
        <Block title="الإجراء المقترح" body={item.recommendedAction} />
        {item.ifIgnored !== "—" ? (
          <Block title="تأثير تجاهل الخطر" body={item.ifIgnored} />
        ) : null}
        <Block title="الدليل" body={item.evidenceSummary} muted />
      </div>
    </article>
  );
}

function Row({
  label,
  value,
  emphasis,
}: {
  label: string;
  value: string;
  emphasis?: boolean;
}) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="shrink-0 text-muted">{label}</dt>
      <dd
        className={cn(
          "text-end",
          emphasis ? "font-semibold text-black-primary" : "text-black-primary/90",
        )}
      >
        {value}
      </dd>
    </div>
  );
}

function Block({
  title,
  body,
  muted,
}: {
  title: string;
  body: string;
  muted?: boolean;
}) {
  if (!body || body === "—") return null;
  return (
    <div>
      <p className="mb-1 text-xs font-semibold text-muted">{title}</p>
      <p className={cn("leading-relaxed", muted ? "text-muted" : "text-black-primary/90")}>
        {body}
      </p>
    </div>
  );
}
