"use client";

import { cn } from "@/lib/utils";
import type { RiskMatrixItemView } from "@/lib/risk/view-types";

const likelihoodLevels = ["منخفض", "متوسط", "مرتفع"] as const;
const impactLevels = ["مرتفع", "متوسط", "منخفض"] as const;

type Likelihood = (typeof likelihoodLevels)[number];
type Impact = (typeof impactLevels)[number];

function cellTone(likelihood: Likelihood, impact: Impact) {
  const score =
    likelihoodLevels.indexOf(likelihood) + impactLevels.indexOf(impact);
  if (score >= 4) {
    return "bg-destructive/10 border-destructive/25";
  }
  if (score >= 2) {
    return "bg-warning/10 border-warning/25";
  }
  return "bg-success/10 border-success/25";
}

function priorityVariant(priority: string) {
  if (priority === "عالية") {
    return "border-destructive/30 bg-destructive/5 text-destructive";
  }
  if (priority === "متوسطة") {
    return "border-warning/30 bg-warning/5 text-warning";
  }
  return "border-success/30 bg-success/5 text-success";
}

function getItemsInCell(
  items: RiskMatrixItemView[],
  likelihood: Likelihood,
  impact: Impact,
) {
  return items.filter(
    (item) => item.likelihood === likelihood && item.impact === impact,
  );
}

export interface RiskPriorityMatrixProps {
  items: RiskMatrixItemView[];
  className?: string;
  selectedId?: string | null;
  onSelectItem?: (id: string) => void;
}

export function RiskPriorityMatrix({
  items,
  className,
  selectedId,
  onSelectItem,
}: RiskPriorityMatrixProps) {
  return (
    <article
      className={cn(
        "rounded-2xl border border-border/60 bg-surface px-5 py-5 md:px-6 md:py-5",
        className,
      )}
    >
      <div className="mb-6 space-y-1.5">
        <h3 className="text-xl font-semibold tracking-tight text-black-primary md:text-[1.35rem]">
          مصفوفة أولوية المخاطر
        </h3>
        <p className="text-sm leading-relaxed text-muted md:text-[15px]">
          تصنيف النتائج حسب احتمالية الحدوث وتأثيرها — من التحليل الحتمي
        </p>
      </div>

      <div className="overflow-x-auto">
        <div className="min-w-[640px]">
          <div className="mb-3 grid grid-cols-[88px_repeat(3,minmax(0,1fr))] gap-2">
            <div />
            {likelihoodLevels.map((level) => (
              <div
                key={level}
                className="text-center text-xs font-semibold tracking-wide text-muted"
              >
                {level}
              </div>
            ))}
          </div>

          <div className="space-y-2">
            {impactLevels.map((impact) => (
              <div
                key={impact}
                className="grid grid-cols-[88px_repeat(3,minmax(0,1fr))] gap-2"
              >
                <div className="flex items-center justify-end pe-3 text-xs font-semibold text-muted">
                  {impact}
                </div>
                {likelihoodLevels.map((likelihood) => {
                  const cellItems = getItemsInCell(items, likelihood, impact);
                  return (
                    <MatrixCell
                      key={`${impact}-${likelihood}`}
                      likelihood={likelihood}
                      impact={impact}
                      items={cellItems}
                      selectedId={selectedId}
                      onSelectItem={onSelectItem}
                    />
                  );
                })}
              </div>
            ))}
          </div>

          <div className="mt-6 flex flex-wrap items-center gap-4 text-xs text-muted">
            <span className="font-medium text-gray-medium">التأثير ←</span>
            <span className="inline-flex items-center gap-1.5">
              <span className="h-3 w-3 rounded border border-destructive/30 bg-destructive/10" />
              حرج
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="h-3 w-3 rounded border border-warning/30 bg-warning/10" />
              متوسط
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="h-3 w-3 rounded border border-success/30 bg-success/10" />
              منخفض
            </span>
          </div>
        </div>
      </div>
    </article>
  );
}

interface MatrixCellProps {
  likelihood: Likelihood;
  impact: Impact;
  items: RiskMatrixItemView[];
  selectedId?: string | null;
  onSelectItem?: (id: string) => void;
}

function MatrixCell({
  likelihood,
  impact,
  items,
  selectedId,
  onSelectItem,
}: MatrixCellProps) {
  return (
    <div
      className={cn(
        "min-h-[72px] rounded-xl border p-2.5 transition-colors",
        cellTone(likelihood, impact),
      )}
    >
      <div className="flex flex-wrap gap-1.5">
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onSelectItem?.(item.id)}
            className={cn(
              "rounded-full border px-2.5 py-1 text-[11px] font-semibold leading-tight text-start transition-colors",
              priorityVariant(item.priority),
              selectedId === item.id && "ring-2 ring-gold-primary/40",
            )}
            title={`${item.name}\n${item.whyTooltip}\n${item.department} · ${item.amountExposed}\nانقر للتفاصيل التنفيذية`}
          >
            <span className="block truncate max-w-[140px]">{item.name}</span>
            <span className="block text-[10px] font-normal opacity-80">{item.department}</span>
            {item.amountExposed !== "—" ? (
              <span className="block text-[10px] font-normal opacity-90">{item.amountExposed}</span>
            ) : null}
          </button>
        ))}
      </div>
    </div>
  );
}
