import { cn } from "@/lib/utils";

export interface DashboardStatCardProps {
  label: string;
  value: React.ReactNode;
  hint?: string;
  departmentBadge?: string;
  icon?: React.ReactNode;
  trend?: React.ReactNode;
  emphasis?: boolean;
  className?: string;
}

export function DashboardStatCard({
  label,
  value,
  hint,
  departmentBadge,
  icon,
  trend,
  emphasis = false,
  className,
}: DashboardStatCardProps) {
  return (
    <article
      className={cn(
        "group flex flex-col rounded-2xl border border-border/60 bg-surface px-6 py-6 transition-colors hover:border-gold-primary/25 md:px-7 md:py-7",
        emphasis ? "min-h-[188px] md:min-h-[204px]" : "min-h-[168px] md:min-h-[180px]",
        className,
      )}
    >
      <div className="mb-4 flex items-start justify-end">
        {icon ? (
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-bg-light text-gold-primary/70">
            {icon}
          </span>
        ) : null}
      </div>

      <div className="flex flex-1 flex-col justify-end space-y-2.5">
        <p
          className={cn(
            "break-words font-semibold leading-none tracking-tight text-black-primary",
            emphasis
              ? "text-[clamp(1.875rem,2.4vw,3rem)]"
              : "text-[clamp(1.5rem,2vw,2.5rem)]",
          )}
        >
          {value}
        </p>
        <p
          className={cn(
            "font-medium leading-snug text-muted",
            emphasis ? "text-xs" : "text-sm",
          )}
        >
          {label}
        </p>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 pt-1">
          {departmentBadge ? (
            <span className="text-[11px] font-medium text-gold-dark/75">
              {departmentBadge}
            </span>
          ) : null}
          {hint ? (
            <span className="text-xs text-muted">{hint}</span>
          ) : null}
          {trend ? (
            <span className="text-xs font-medium text-gray-medium">{trend}</span>
          ) : null}
        </div>
      </div>
    </article>
  );
}
