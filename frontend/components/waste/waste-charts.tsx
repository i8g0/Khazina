"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  XAxis,
  YAxis,
} from "recharts";
import { ChartContainer, chartTheme } from "@/components/ui/chart-container";
import { wasteByCategory, wasteTrend } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

function formatWaste(value: number) {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(0)}K`;
  }
  return value.toString();
}

interface WasteChartCardProps {
  title: string;
  description: string;
  children: React.ReactNode;
  height?: number;
}

function WasteChartCard({
  title,
  description,
  children,
  height = 360,
}: WasteChartCardProps) {
  return (
    <article className="rounded-2xl border border-border/60 bg-surface">
      <div className="space-y-1 border-b border-border/60 px-5 py-3.5">
        <h3 className="text-base font-semibold tracking-tight text-black-primary md:text-[1.1rem]">
          {title}
        </h3>
        <p className="text-sm leading-relaxed text-muted">
          {description}
        </p>
      </div>
      <div className="px-2 py-2 md:px-2.5 md:py-2.5">
        <div
          className={cn("w-full overflow-hidden rounded-xl bg-bg-light/30 px-1 py-1.5")}
          style={{ minHeight: height }}
        >
          {children}
        </div>
      </div>
    </article>
  );
}

export function WasteCharts() {
  return (
    <div className="grid gap-5 xl:grid-cols-2 xl:gap-6">
      <WasteChartCard
        title="اتجاه الهدر المالي الشهري"
        description="تطور الهدر المكتشف خلال الأشهر الستة الأخيرة"
        height={360}
      >
        <ChartContainer height={360}>
          <LineChart
            data={wasteTrend}
            margin={{ top: 8, right: 12, left: 4, bottom: 4 }}
          >
            <CartesianGrid stroke={chartTheme.grid} vertical={false} />
            <XAxis
              dataKey="month"
              tick={{ fill: chartTheme.text, fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: chartTheme.text, fontSize: 12 }}
              tickFormatter={formatWaste}
              axisLine={false}
              tickLine={false}
            />
            <Line
              type="monotone"
              dataKey="waste"
              stroke={chartTheme.primary}
              strokeWidth={2.5}
              dot={{ fill: chartTheme.primary, r: 4, strokeWidth: 0 }}
              activeDot={{ r: 5, fill: chartTheme.primary }}
              name="الهدر"
            />
          </LineChart>
        </ChartContainer>
      </WasteChartCard>

      <WasteChartCard
        title="الهدر حسب الفئة"
        description="توزيع الهدر المالي على فئات الإنفاق الرئيسية"
        height={360}
      >
        <ChartContainer height={360}>
          <BarChart
            data={wasteByCategory}
            layout="vertical"
            margin={{ top: 8, right: 12, left: 4, bottom: 4 }}
          >
            <CartesianGrid stroke={chartTheme.grid} horizontal={false} />
            <XAxis
              type="number"
              tick={{ fill: chartTheme.text, fontSize: 12 }}
              tickFormatter={formatWaste}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="category"
              width={130}
              tick={{ fill: chartTheme.text, fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <Bar
              dataKey="waste"
              fill={chartTheme.primary}
              radius={[0, 6, 6, 0]}
              barSize={22}
              name="الهدر"
            />
          </BarChart>
        </ChartContainer>
      </WasteChartCard>
    </div>
  );
}
