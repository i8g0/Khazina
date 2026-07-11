import { cn } from "@/lib/utils";
import { wasteByDepartment } from "@/lib/placeholder-data";

function formatAmount(value: number) {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)}M ر.س`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(0)}K ر.س`;
  }
  return `${value} ر.س`;
}

export function WasteDepartmentBreakdown({ className }: { className?: string }) {
  const maxWaste = Math.max(...wasteByDepartment.map((item) => item.waste));

  return (
    <div className={cn("space-y-4", className)}>
      {wasteByDepartment.map((item) => {
        const width = `${Math.round((item.waste / maxWaste) * 100)}%`;

        return (
          <div
            key={item.department}
            className="rounded-2xl border border-border/60 bg-surface px-5 py-4 md:px-6 md:py-5"
          >
            <div className="mb-3 flex items-center justify-between gap-4">
              <p className="text-sm font-semibold text-black-primary">
                {item.department}
              </p>
              <p className="text-sm font-semibold tabular-nums text-gold-dark">
                {formatAmount(item.waste)}
              </p>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-bg-light">
              <div
                className="h-full rounded-full bg-gold-primary transition-all"
                style={{ width }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
