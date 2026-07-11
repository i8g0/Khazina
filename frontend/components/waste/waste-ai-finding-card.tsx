import { BrainCircuit } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { WasteRecommendation } from "@/lib/placeholder-data";

export interface WasteAiFindingCardProps {
  item: WasteRecommendation;
  className?: string;
}

export function WasteAiFindingCard({ item, className }: WasteAiFindingCardProps) {
  const isHigh = item.badge === "عالية";

  return (
    <article
      className={cn(
        "flex h-full flex-col rounded-2xl border border-border/60 bg-surface px-5 py-5 md:px-6 md:py-6",
        className,
      )}
    >
      <div className="mb-5 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gold-primary/10 text-gold-dark">
            <BrainCircuit className="h-[18px] w-[18px]" strokeWidth={1.75} />
          </span>
          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-gold-dark">
            نتيجة ذكاء اصطناعي
          </span>
        </div>
        <Badge
          variant={isHigh ? "warning" : "secondary"}
          className="px-3 py-1 text-xs font-semibold"
        >
          {item.badge}
        </Badge>
      </div>

      <h3 className="mb-2 text-xl font-semibold leading-snug tracking-tight text-black-primary">
        {item.title}
      </h3>
      <p className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-gold-dark">
        {item.department}
      </p>
      <p className="flex-1 text-sm leading-7 text-muted md:text-[15px]">
        {item.description}
      </p>
      <div className="mt-6 border-t border-border/60 pt-4">
        <p className="text-sm font-medium text-gray-medium">
          ثقة{" "}
          <span className="font-semibold text-black-primary">{item.confidence}</span>
        </p>
      </div>
    </article>
  );
}
