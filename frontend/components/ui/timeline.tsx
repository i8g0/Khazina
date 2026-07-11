import { cn } from "@/lib/utils";
import {
  TimelineItem,
  type TimelineItemProps,
} from "@/components/ui/timeline-item";

export type TimelineEventData = Omit<TimelineItemProps, "isLast">;

export interface TimelineProps {
  events: TimelineEventData[];
  maxVisible?: number;
  className?: string;
}

export function Timeline({
  events,
  maxVisible = 5,
  className,
}: TimelineProps) {
  const visibleEvents = events.slice(0, maxVisible);

  if (visibleEvents.length === 0) {
    return null;
  }

  return (
    <ol className={cn("space-y-0", className)}>
      {visibleEvents.map((event, index) => (
        <TimelineItem
          key={event.id}
          {...event}
          isLast={index === visibleEvents.length - 1}
        />
      ))}
    </ol>
  );
}
