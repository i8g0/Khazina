import { Badge } from "@/components/ui/badge";
import type { RiskRecommendationView } from "@/lib/risk/view-types";
import { cn } from "@/lib/utils";

export interface RiskRecommendationCardProps {
  item: RiskRecommendationView;
  className?: string;
}

export function RiskRecommendationCard({
  item,
  className,
}: RiskRecommendationCardProps) {
  const isHigh = item.priority === "عالية";

  return (
    <article
      className={cn(
        "flex h-full min-h-[220px] flex-col rounded-2xl border border-border/60 bg-surface px-5 py-5 transition-colors hover:border-gold-primary/25 md:px-6 md:py-6",
        className,
      )}
    >
      <Badge
        variant={isHigh ? "warning" : "secondary"}
        className="mb-3.5 w-fit px-3 py-1 text-xs font-semibold"
      >
        {item.priority}
      </Badge>

      <h3 className="mb-2 text-xl font-semibold leading-snug tracking-tight text-black-primary md:text-[1.35rem]">
        {item.title}
      </h3>

      {item.category ? (
        <p className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-gold-dark">
          {item.category}
        </p>
      ) : null}

      <p className="mb-4 flex-1 text-sm leading-6 text-muted md:text-[15px]">
        {item.description}
      </p>
    </article>
  );
}
