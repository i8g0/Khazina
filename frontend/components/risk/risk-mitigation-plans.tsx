import { ClipboardCheck, Clock, User } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { RiskMitigationPlanView } from "@/lib/risk/view-types";
import { cn } from "@/lib/utils";

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("ar-SA", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function statusVariant(status: string) {
  if (status === "قيد التنفيذ") {
    return "warning" as const;
  }
  if (status === "قيد المراجعة") {
    return "default" as const;
  }
  return "secondary" as const;
}

export interface RiskMitigationPlansProps {
  plans: RiskMitigationPlanView[];
  className?: string;
}

export function RiskMitigationPlans({ plans, className }: RiskMitigationPlansProps) {
  return (
    <ol className={cn("space-y-0", className)}>
      {plans.map((plan, index) => (
        <MitigationPlanItem
          key={plan.id}
          plan={plan}
          isLast={index === plans.length - 1}
        />
      ))}
    </ol>
  );
}

interface MitigationPlanItemProps {
  plan: RiskMitigationPlanView;
  isLast: boolean;
}

function MitigationPlanItem({ plan, isLast }: MitigationPlanItemProps) {
  return (
    <li className="relative flex gap-4 pb-5 last:pb-0">
      {!isLast ? (
        <span
          aria-hidden="true"
          className="absolute start-[17px] top-9 h-[calc(100%-1.25rem)] w-px bg-border/70"
        />
      ) : null}
      <span className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-gold-primary/30 bg-gold-primary/10 text-gold-dark">
        <ClipboardCheck className="h-[18px] w-[18px] stroke-[1.75]" aria-hidden="true" />
      </span>
      <article className="min-w-0 flex-1 rounded-2xl border border-border/60 bg-surface px-5 py-4 md:px-6 md:py-5">
        <div className="mb-3 flex flex-wrap items-center gap-2.5">
          <Badge
            variant={statusVariant(plan.status)}
            className="px-3 py-1 text-xs font-semibold"
          >
            {plan.status}
          </Badge>
          <span className="rounded-full border border-border/70 bg-bg-light px-2.5 py-0.5 text-[11px] font-medium text-gray-medium">
            {plan.relatedRisk}
          </span>
        </div>
        <h3 className="mb-2 text-[15px] font-semibold leading-snug text-black-primary md:text-base">
          {plan.title}
        </h3>
        <p className="mb-3.5 text-sm leading-6 text-muted md:text-[15px]">
          {plan.description}
        </p>
        <div className="flex flex-wrap gap-4 border-t border-border/60 pt-3.5 text-xs text-muted">
          <span className="inline-flex items-center gap-1.5">
            <User className="h-3.5 w-3.5" strokeWidth={1.75} />
            {plan.owner}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Clock className="h-3.5 w-3.5" strokeWidth={1.75} />
            {formatDate(plan.targetDate)}
          </span>
        </div>
      </article>
    </li>
  );
}
