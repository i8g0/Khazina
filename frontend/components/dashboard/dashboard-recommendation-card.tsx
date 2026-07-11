import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

const recommendationDepartments: Record<string, string> = {
  "rec-w01": "المشتريات",
  "rec-w02": "العمليات",
  "rec-w03": "تقنية المعلومات",
};

export interface DashboardRecommendationCardProps {
  id: string;
  title: string;
  description: string;
  badge: string;
  confidence: string;
  className?: string;
}

export function DashboardRecommendationCard({
  id,
  title,
  description,
  badge,
  confidence,
  className,
}: DashboardRecommendationCardProps) {
  const department = recommendationDepartments[id];
  const isHigh = badge === "عالية";

  return (
    <article
      className={cn(
        "flex h-full flex-col rounded-2xl border border-border/60 bg-surface px-7 py-7 transition-colors hover:border-gold-primary/25 md:px-8 md:py-8",
        className,
      )}
    >
      <Badge
        variant={isHigh ? "warning" : "secondary"}
        className="mb-5 w-fit px-3 py-1 text-xs font-semibold"
      >
        {badge}
      </Badge>

      <h3 className="mb-2 text-xl font-semibold leading-snug tracking-tight text-black-primary md:text-[1.35rem]">
        {title}
      </h3>

      {department ? (
        <p className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-gold-dark">
          {department}
        </p>
      ) : null}

      <p className="mb-6 flex-1 text-sm leading-7 text-muted md:text-[15px]">
        {description}
      </p>

      <div className="border-t border-border/60 pt-4">
        <p className="text-sm font-medium text-gray-medium">
          ثقة <span className="font-semibold text-black-primary">{confidence}</span>
        </p>
      </div>
    </article>
  );
}
