import type { SimulationAssumption } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

export interface SimulationAssumptionsProps {
  assumptions: SimulationAssumption[];
  className?: string;
}

export function SimulationAssumptions({
  assumptions,
  className,
}: SimulationAssumptionsProps) {
  return (
    <article
      className={cn(
        "rounded-2xl border border-border/60 bg-surface px-7 py-7 md:px-8 md:py-8",
        className,
      )}
    >
      <div className="mb-6 space-y-2">
        <h3 className="text-xl font-semibold tracking-tight text-black-primary md:text-[1.35rem]">
          افتراضات السيناريو
        </h3>
        <p className="text-sm leading-relaxed text-muted md:text-[15px]">
          معاملات المحاكاة الحالية — للعرض فقط
        </p>
      </div>
      <dl className="grid gap-4 sm:grid-cols-2">
        {assumptions.map((item) => (
          <div
            key={item.label}
            className="rounded-xl border border-border/60 bg-bg-light/40 px-5 py-4"
          >
            <dt className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-muted">
              {item.label}
            </dt>
            <dd className="text-base font-semibold text-black-primary">{item.value}</dd>
          </div>
        ))}
      </dl>
    </article>
  );
}
