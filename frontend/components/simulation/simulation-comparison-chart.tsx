"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  XAxis,
  YAxis,
} from "recharts";
import { ChartContainer, chartTheme } from "@/components/ui/chart-container";
import type { SimulationChartPoint } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

function formatAmount(value: number) {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(0)}K`;
  }
  return value.toString();
}

export interface SimulationComparisonChartProps {
  data: SimulationChartPoint[];
  className?: string;
}

export function SimulationComparisonChart({
  data,
  className,
}: SimulationComparisonChartProps) {
  return (
    <article
      className={cn("rounded-2xl border border-border/60 bg-surface", className)}
    >
      <div className="space-y-1 border-b border-border/60 px-5 py-3.5">
        <h3 className="text-base font-semibold tracking-tight text-black-primary md:text-[1.1rem]">
          مقارنة الأساس مقابل المتوقع
        </h3>
        <p className="text-sm leading-relaxed text-muted">
          توزيع الأثر المالي على الأرباع الثلاثة القادمة
        </p>
      </div>
      <div className="px-2 py-2 md:px-2.5 md:py-2.5">
        <div className="overflow-hidden rounded-xl bg-bg-light/30 px-1 py-1.5">
          <ChartContainer height={380}>
            <BarChart
              data={data}
              margin={{ top: 8, right: 12, left: 4, bottom: 4 }}
            >
              <CartesianGrid stroke={chartTheme.grid} vertical={false} />
              <XAxis
                dataKey="quarter"
                tick={{ fill: chartTheme.text, fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: chartTheme.text, fontSize: 12 }}
                tickFormatter={formatAmount}
                axisLine={false}
                tickLine={false}
              />
              <Legend
                wrapperStyle={{ paddingTop: 16 }}
                formatter={(value) =>
                  value === "baseline" ? "الأساس" : "المتوقع"
                }
              />
              <Bar
                dataKey="baseline"
                fill={chartTheme.text}
                radius={[6, 6, 0, 0]}
                barSize={36}
                name="baseline"
              />
              <Bar
                dataKey="projected"
                fill={chartTheme.primary}
                radius={[6, 6, 0, 0]}
                barSize={36}
                name="projected"
              />
            </BarChart>
          </ChartContainer>
        </div>
      </div>
    </article>
  );
}
