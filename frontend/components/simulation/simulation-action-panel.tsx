import { ArrowRight, ClipboardList } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { SimulationActionItem } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

export interface SimulationActionPanelProps {
  items: SimulationActionItem[];
  className?: string;
}

export function SimulationActionPanel({
  items,
  className,
}: SimulationActionPanelProps) {
  return (
    <div className={cn("grid gap-6 lg:grid-cols-3 lg:gap-7", className)}>
      {items.map((item) => (
        <article
          key={item.id}
          className="flex min-h-[196px] flex-col rounded-2xl border border-border/60 bg-surface px-7 py-8 md:px-8 md:py-9"
        >
          <div className="mb-5 flex items-center justify-between gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gold-primary/10 text-gold-dark">
              <ClipboardList className="h-[18px] w-[18px]" strokeWidth={1.75} />
            </span>
            <Badge variant="outline" className="px-3 py-1 text-xs font-semibold">
              {item.status}
            </Badge>
          </div>
          <h3 className="mb-3 text-lg font-semibold leading-snug text-black-primary">
            {item.title}
          </h3>
          <p className="mb-6 flex-1 text-sm leading-7 text-muted md:text-[15px]">
            {item.description}
          </p>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-gold-dark">
            <span>إجراء مقترح</span>
            <ArrowRight className="h-3.5 w-3.5" strokeWidth={1.75} />
          </div>
        </article>
      ))}
    </div>
  );
}
