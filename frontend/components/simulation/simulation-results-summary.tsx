import { BarChart3, LineChart, TrendingDown, TrendingUp } from "lucide-react";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { Alert } from "@/components/ui/alert";
import type { SimulationForecast, SimulationResultSummary } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

export interface SimulationResultsSummaryProps {
  forecast: SimulationForecast;
  summary: SimulationResultSummary;
  className?: string;
}

export function SimulationResultsSummary({
  forecast,
  summary,
  className,
}: SimulationResultsSummaryProps) {
  const isPositiveDelta = forecast.deltaValue.startsWith("+");
  const DeltaIcon = isPositiveDelta ? TrendingUp : TrendingDown;

  return (
    <div className={cn("space-y-8", className)}>
      <section className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3 xl:gap-7">
        <DashboardStatCard
          label={forecast.baselineLabel}
          value={forecast.baselineValue}
          hint={`ثقة ${forecast.confidence}`}
          emphasis
          icon={<BarChart3 className="h-[17px] w-[17px]" strokeWidth={1.75} />}
        />
        <DashboardStatCard
          label={forecast.projectedLabel}
          value={forecast.projectedValue}
          hint="بعد تطبيق السيناريو"
          emphasis
          icon={<LineChart className="h-[17px] w-[17px]" strokeWidth={1.75} />}
        />
        <DashboardStatCard
          label={forecast.deltaLabel}
          value={forecast.deltaValue}
          hint={isPositiveDelta ? "زيادة متوقعة" : "انخفاض متوقع"}
          emphasis
          icon={<DeltaIcon className="h-[17px] w-[17px]" strokeWidth={1.75} />}
        />
      </section>

      <Alert variant="info" title={summary.title}>
        {summary.description}
      </Alert>
    </div>
  );
}
