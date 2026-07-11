import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import type { DataValidationItem } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";
import { CheckCircle2, ClipboardCheck, Copy, ShieldCheck } from "lucide-react";

const validationIcons = [ClipboardCheck, ShieldCheck, CheckCircle2, Copy];

export interface DataSummaryCardsProps {
  validationItems: DataValidationItem[];
  className?: string;
}

export function DataSummaryCards({
  validationItems,
  className,
}: DataSummaryCardsProps) {
  return (
    <div className={cn("grid gap-6 sm:grid-cols-2 xl:grid-cols-4 xl:gap-7", className)}>
      {validationItems.map((item, index) => {
        const Icon = validationIcons[index];
        return (
          <DashboardStatCard
            key={item.check}
            label={item.check}
            value={item.result}
            hint={item.details}
            emphasis
            icon={<Icon className="h-[17px] w-[17px]" strokeWidth={1.75} />}
          />
        );
      })}
    </div>
  );
}
