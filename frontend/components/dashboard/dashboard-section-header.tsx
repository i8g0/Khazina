import { cn } from "@/lib/utils";

export interface DashboardSectionHeaderProps {
  title: string;
  description?: string;
  /** Experimental compact scale (Dashboard density test only) */
  dense?: boolean;
  className?: string;
}

export function DashboardSectionHeader({
  title,
  description,
  dense = false,
  className,
}: DashboardSectionHeaderProps) {
  return (
    <div className={cn("space-y-1.5", className)}>
      <h2
        className={cn(
          "font-semibold tracking-tight text-black-primary",
          dense
            ? "text-[1.35rem] md:text-[1.5rem]"
            : "text-[1.5rem] md:text-[1.65rem]",
        )}
      >
        {title}
      </h2>
      {description ? (
        <p className="max-w-3xl text-[15px] leading-relaxed text-muted md:text-base">
          {description}
        </p>
      ) : null}
    </div>
  );
}
