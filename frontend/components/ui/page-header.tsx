import { cn } from "@/lib/utils";

export interface PageHeaderProps {
  title: string;
  description?: string;
  meta?: React.ReactNode;
  actions?: React.ReactNode;
  compact?: boolean;
  className?: string;
}

export function PageHeader({
  title,
  description,
  meta,
  actions,
  compact = false,
  className,
}: PageHeaderProps) {
  return (
    <header
      className={cn(
        "border-b border-border/60",
        compact ? "pb-4 md:pb-5" : "pb-5 md:pb-6",
        className,
      )}
    >
      <div
        className={cn(
          "flex flex-col lg:flex-row lg:items-center lg:justify-between",
          compact ? "gap-3" : "gap-4 lg:items-end",
        )}
      >
        <div className={cn("max-w-3xl", compact ? "space-y-1.5" : "space-y-2")}>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1
              className={cn(
                "font-semibold tracking-tight text-black-primary",
                compact
                  ? "text-[1.65rem] leading-tight md:text-[1.85rem]"
                  : "text-[2.25rem] leading-tight md:text-[2.75rem]",
              )}
            >
              {title}
            </h1>
            {meta}
          </div>
          {description ? (
            <p
              className={cn(
                "leading-relaxed text-gray-medium",
                compact ? "text-sm md:text-[15px]" : "text-base md:text-lg",
              )}
            >
              {description}
            </p>
          ) : null}
        </div>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </div>
    </header>
  );
}
