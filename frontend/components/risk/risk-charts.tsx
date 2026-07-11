"use client";

import { Bar, BarChart, CartesianGrid, Cell, XAxis, YAxis } from "recharts";
import { ChartContainer, chartTheme } from "@/components/ui/chart-container";
import { riskByDepartment, riskBySeverity } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

interface RiskChartCardProps {
  title: string;
  description: string;
  children: React.ReactNode;
  height?: number;
}

function RiskChartCard({
  title,
  description,
  children,
  height = 360,
}: RiskChartCardProps) {
  return (
    <article className="rounded-2xl border border-border/60 bg-surface">
      <div className="space-y-3 border-b border-border/60 px-8 py-8 md:px-9 md:py-9">
        <h3 className="text-xl font-semibold tracking-tight text-black-primary md:text-[1.35rem]">
          {title}
        </h3>
        <p className="text-sm leading-relaxed text-muted md:text-[15px]">
          {description}
        </p>
      </div>
      <div className="px-7 py-8 md:px-9 md:py-10">
        <div
          className={cn(
            "w-full overflow-hidden rounded-xl bg-bg-light/30 px-5 py-6 md:px-6 md:py-7",
          )}
          style={{ minHeight: height }}
        >
          {children}
        </div>
      </div>
    </article>
  );
}

const severityColors: Record<string, string> = {
  عالية: "#C0392B",
  متوسطة: "#D4A017",
  منخفضة: "#27AE60",
};

export function RiskCharts() {
  return (
    <div className="grid gap-8 xl:grid-cols-2 xl:gap-10">
      <RiskChartCard
        title="توزيع المخاطر حسب القسم"
        description="مؤشر خطورة المخاطر النشطة لكل إدارة"
        height={360}
      >
        <ChartContainer height={360}>
          <BarChart
            data={riskByDepartment}
            layout="vertical"
            margin={{ top: 20, right: 28, left: 12, bottom: 20 }}
          >
            <CartesianGrid stroke={chartTheme.grid} horizontal={false} />
            <XAxis
              type="number"
              domain={[0, 100]}
              tick={{ fill: chartTheme.text, fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="department"
              width={130}
              tick={{ fill: chartTheme.text, fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <Bar
              dataKey="score"
              fill={chartTheme.primary}
              radius={[0, 6, 6, 0]}
              barSize={22}
              name="مؤشر الخطورة"
            />
          </BarChart>
        </ChartContainer>
      </RiskChartCard>

      <RiskChartCard
        title="توزيع المخاطر حسب مستوى الخطورة"
        description="عدد المخاطر النشطة لكل مستوى أولوية"
        height={360}
      >
        <ChartContainer height={360}>
          <BarChart
            data={riskBySeverity}
            margin={{ top: 20, right: 28, left: 12, bottom: 20 }}
          >
            <CartesianGrid stroke={chartTheme.grid} vertical={false} />
            <XAxis
              dataKey="level"
              tick={{ fill: chartTheme.text, fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fill: chartTheme.text, fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Bar dataKey="count" radius={[6, 6, 0, 0]} barSize={48} name="عدد المخاطر">
              {riskBySeverity.map((entry) => (
                <Cell
                  key={entry.level}
                  fill={severityColors[entry.level] ?? chartTheme.primary}
                />
              ))}
            </Bar>
          </BarChart>
        </ChartContainer>
      </RiskChartCard>
    </div>
  );
}
