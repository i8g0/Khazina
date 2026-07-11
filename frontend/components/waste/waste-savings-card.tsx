import { PiggyBank } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { WasteRecommendation } from "@/lib/placeholder-data";

export interface WasteSavingsCardProps {
  item: WasteRecommendation;
  className?: string;
}

export function WasteSavingsCard({ item, className }: WasteSavingsCardProps) {
  const isHigh = item.badge === "عالية";

  return (
    <article
      className={cn(
        "flex h-full flex-col rounded-2xl border border-border/60 bg-surface px-5 py-5 transition-colors hover:border-gold-primary/25 md:px-6 md:py-6",
        className,
      )}
    >
      <Badge
        variant={isHigh ? "warning" : "secondary"}
        className="mb-5 w-fit px-3 py-1 text-xs font-semibold"
      >
        {item.badge}
      </Badge>

      <h3 className="mb-2 text-xl font-semibold leading-snug tracking-tight text-black-primary md:text-[1.35rem]">
        {item.title}
      </h3>
      <p className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-gold-dark">
        {item.department}
      </p>
      <p className="mb-6 flex-1 text-sm leading-7 text-muted md:text-[15px]">
        {item.description}
      </p>

      <div className="border-t border-border/60 pt-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm font-medium text-gray-medium">
            <PiggyBank className="h-4 w-4 text-gold-dark" strokeWidth={1.75} />
            <span>
              توفير متوقع{" "}
              <span className="font-semibold text-black-primary">
                {item.savings} ر.س
              </span>
            </span>
          </div>
          <span className="text-xs font-medium text-muted">ثقة {item.confidence}</span>
        </div>
      </div>
    </article>
  );
}
