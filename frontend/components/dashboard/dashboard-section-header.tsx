import { cn } from "@/lib/utils";

export interface DashboardSectionHeaderProps {
  title: string;
  description?: string;
  className?: string;
}

export function DashboardSectionHeader({
  title,
  description,
  className,
}: DashboardSectionHeaderProps) {
  return (
    <div className={cn("space-y-2.5", className)}>
      <h2 className="text-[1.65rem] font-semibold tracking-tight text-black-primary md:text-[1.875rem]">
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
