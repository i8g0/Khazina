import { cn } from "@/lib/utils";

export interface TimelineItemProps {
  id: string;
  date: string;
  title: string;
  type: string;
  description?: string;
  isLast?: boolean;
}

export function TimelineItem({
  date,
  title,
  type,
  description,
  isLast = false,
}: TimelineItemProps) {
  const isAlert = type === "تنبيه";

  return (
    <li className="relative flex gap-4 pb-6 last:pb-0">
      {!isLast ? (
        <span
          aria-hidden="true"
          className="absolute start-[7px] top-4 h-[calc(100%-0.5rem)] w-px bg-border"
        />
      ) : null}
      <span
        className={cn(
          "relative mt-1.5 h-3.5 w-3.5 shrink-0 rounded-full border-2 border-surface",
          isAlert ? "bg-gold-primary" : "bg-gray-medium",
        )}
      />
      <div className="min-w-0 flex-1 space-y-1">
        <div className="flex flex-wrap items-center gap-2">
          <time dateTime={date} className="text-xs text-muted">
            {date}
          </time>
          <span className="rounded-full bg-bg-light px-2 py-0.5 text-xs text-gray-medium">
            {type}
          </span>
        </div>
        <p className="text-sm font-medium text-black-primary">{title}</p>
        {description ? (
          <p className="text-xs leading-relaxed text-muted">{description}</p>
        ) : null}
      </div>
    </li>
  );
}
