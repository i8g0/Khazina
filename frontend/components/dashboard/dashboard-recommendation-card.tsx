import Link from "next/link";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export interface DashboardRecommendationCardProps {
  id: string;
  title: string;
  description: string;
  badge: string;
  confidence: string;
  href?: string;
  className?: string;
}

export function DashboardRecommendationCard({
  id,
  title,
  description,
  badge,
  confidence,
  href,
  className,
}: DashboardRecommendationCardProps) {
  const isHigh = badge === "عالية";

  const card = (
    <article
      className={cn(
        "flex h-full flex-col rounded-2xl border border-border/60 bg-surface px-5 py-5 transition-colors hover:border-gold-primary/25 md:px-6 md:py-6",
        href && "cursor-pointer",
        className,
      )}
    >
      <Badge
        variant={isHigh ? "warning" : "secondary"}
        className="mb-3.5 w-fit px-3 py-1 text-xs font-semibold"
      >
        {badge}
      </Badge>

      <h3 className="mb-2 text-xl font-semibold leading-snug tracking-tight text-black-primary md:text-[1.35rem]">
        {title}
      </h3>

      <p className="mb-4 flex-1 text-sm leading-6 text-muted md:text-[15px]">
        {description}
      </p>

      <div className="border-t border-border/60 pt-3.5">
        <p className="text-sm font-medium text-gray-medium">
          ثقة <span className="font-semibold text-black-primary">{confidence}</span>
        </p>
      </div>
    </article>
  );

  if (href) {
    return (
      <Link key={id} href={href} className="block h-full">
        {card}
      </Link>
    );
  }

  return card;
}
