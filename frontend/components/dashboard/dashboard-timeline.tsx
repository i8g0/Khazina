import {
  AlertTriangle,
  BarChart3,
  ClipboardCheck,
  FileText,
  Settings2,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { TimelineEvent } from "@/lib/placeholder-data";

const typeIcons: Record<string, LucideIcon> = {
  تنبيه: AlertTriangle,
  تحليل: BarChart3,
  مراجعة: ClipboardCheck,
  نظام: Settings2,
  تقرير: FileText,
};

export interface DashboardTimelineProps {
  events: TimelineEvent[];
  maxVisible?: number;
  className?: string;
}

export function DashboardTimeline({
  events,
  maxVisible = 5,
  className,
}: DashboardTimelineProps) {
  const visibleEvents = events.slice(0, maxVisible);

  if (visibleEvents.length === 0) {
    return null;
  }

  return (
    <ol className={cn("space-y-0", className)}>
      {visibleEvents.map((event, index) => {
        const Icon = typeIcons[event.type] ?? FileText;
        const isAlert = event.type === "تنبيه";
        const isLast = index === visibleEvents.length - 1;

        return (
          <li key={event.id} className="relative flex gap-4 pb-5 last:pb-0">
            {!isLast ? (
              <span
                aria-hidden="true"
                className="absolute start-[17px] top-9 h-[calc(100%-1.25rem)] w-px bg-border/70"
              />
            ) : null}
            <span
              className={cn(
                "relative flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border",
                isAlert
                  ? "border-gold-primary/30 bg-gold-primary/10 text-gold-dark"
                  : "border-border/70 bg-bg-light text-gray-medium",
              )}
            >
              <Icon className="h-[18px] w-[18px] stroke-[1.75]" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1 space-y-1.5 pt-0.5">
              <div className="flex flex-wrap items-center gap-2.5">
                <time
                  dateTime={event.date}
                  className="text-xs font-medium tabular-nums text-muted"
                >
                  {event.date}
                </time>
                <span className="rounded-full border border-border/70 bg-bg-light px-2.5 py-0.5 text-[11px] font-medium text-gray-medium">
                  {event.type}
                </span>
              </div>
              <p className="text-[15px] font-medium leading-snug text-black-primary md:text-base">
                {event.title}
              </p>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
