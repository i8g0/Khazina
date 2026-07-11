import { cn } from "@/lib/utils";

export interface DashboardStatCardProps {
  label: string;
  value: React.ReactNode;
  hint?: string;
  departmentBadge?: string;
  icon?: React.ReactNode;
  trend?: React.ReactNode;
  emphasis?: boolean;
  /** Experimental compact scale (Dashboard density test only) */
  dense?: boolean;
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
  dense = false,
  className,
}: DashboardStatCardProps) {
  return (
    <article
      className={cn(
        "group flex flex-col rounded-2xl border border-border/60 bg-surface transition-colors hover:border-gold-primary/25",
        dense ? "px-3.5 py-3 md:px-4 md:py-3" : "px-5 py-5 md:px-6 md:py-5",
        dense
          ? emphasis
            ? "min-h-[104px] md:min-h-[112px]"
            : "min-h-[92px] md:min-h-[100px]"
          : emphasis
            ? "min-h-[150px] md:min-h-[160px]"
            : "min-h-[134px] md:min-h-[144px]",
        className,
      )}
    >
      <div className={cn("flex items-start justify-end", dense ? "mb-1.5" : "mb-3")}>
        {icon ? (
          <span
            className={cn(
              "flex items-center justify-center rounded-lg bg-bg-light text-gold-primary/70",
              dense ? "h-7 w-7" : "h-8 w-8",
            )}
          >
            {icon}
          </span>
        ) : null}
      </div>

      <div
        className={cn(
          "flex flex-1 flex-col justify-end",
          dense ? "space-y-1.5" : "space-y-2",
        )}
      >
        <p
          className={cn(
            "break-words font-semibold leading-none tracking-tight text-black-primary",
            dense
              ? emphasis
                ? "text-[clamp(1.45rem,1.9vw,2.35rem)]"
                : "text-[clamp(1.175rem,1.55vw,1.9rem)]"
              : emphasis
                ? "text-[clamp(1.875rem,2.4vw,3rem)]"
                : "text-[clamp(1.5rem,2vw,2.5rem)]",
          )}
        >
          {value}
        </p>
        <p
          className={cn(
            "font-medium leading-snug text-muted",
            dense
              ? emphasis
                ? "text-[11px]"
                : "text-[13px]"
              : emphasis
                ? "text-xs"
                : "text-sm",
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
