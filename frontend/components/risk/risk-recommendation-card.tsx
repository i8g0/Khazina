import { Badge } from "@/components/ui/badge";
import type { RiskRecommendation } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

const recommendationDepartments: Record<string, string> = {
  "rec-r01": "المشتريات",
  "rec-r02": "الشؤون المالية",
  "rec-r03": "الشؤون المالية",
};

const recommendationConfidence: Record<string, string> = {
  "rec-r01": "91%",
  "rec-r02": "88%",
  "rec-r03": "84%",
};

export interface RiskRecommendationCardProps {
  item: RiskRecommendation;
  className?: string;
}

export function RiskRecommendationCard({
  item,
  className,
}: RiskRecommendationCardProps) {
  const department = recommendationDepartments[item.id];
  const confidence = recommendationConfidence[item.id];
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

      {department ? (
        <p className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-gold-dark">
          {department}
        </p>
      ) : null}

      <p className="mb-4 flex-1 text-sm leading-6 text-muted md:text-[15px]">
        {item.description}
      </p>

      {confidence ? (
        <div className="border-t border-border/60 pt-3.5">
          <p className="text-sm font-medium text-gray-medium">
            ثقة{" "}
            <span className="font-semibold text-black-primary">{confidence}</span>
          </p>
        </div>
      ) : null}
    </article>
  );
}
