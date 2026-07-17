"use client";

import Link from "next/link";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { BarChart3 } from "lucide-react";
import { ChartContainer, chartTheme } from "@/components/ui/chart-container";
import { EmptyState } from "@/components/ui/empty-state";
import { navRouteMap } from "@/lib/app-nav";
import { formatCurrency } from "@/lib/format";

export interface ExecutiveWasteChartProps {
  data: { label: string; amount: number }[];
}

export function ExecutiveWasteChart({ data }: ExecutiveWasteChartProps) {
  if (data.length === 0) {
    return (
      <article className="rounded-2xl border border-border/60 bg-surface">
        <div className="space-y-1 border-b border-border/60 px-5 py-3.5">
          <h3 className="text-base font-semibold tracking-tight text-black-primary md:text-[1.1rem]">
            أعلى الإدارات من حيث الهدر
          </h3>
          <p className="text-sm leading-relaxed text-muted">
            تحديد أين يركز التدخل التنفيذي
          </p>
        </div>
        <div className="flex min-h-[280px] items-center justify-center px-4 py-6">
          <EmptyState
            title="لا بيانات هدر بعد"
            description="نفّذ كشف الهدر لعرض توزيع الإدارات"
            icon={<BarChart3 className="h-6 w-6" />}
            className="border-none bg-transparent shadow-none"
          />
        </div>
      </article>
    );
  }

  const chartData = data.map((row) => ({
    department: row.label,
    amount: row.amount,
    formatted: formatCurrency(row.amount),
  }));

  return (
    <Link href={navRouteMap.waste} className="block">
      <article className="rounded-2xl border border-border/60 bg-surface transition-colors hover:border-gold-primary/25">
        <div className="space-y-1 border-b border-border/60 px-5 py-3.5">
          <h3 className="text-base font-semibold tracking-tight text-black-primary md:text-[1.1rem]">
            أعلى الإدارات من حيث الهدر
          </h3>
          <p className="text-sm leading-relaxed text-muted">
            انقر للانتقال إلى تحليل الهدر التفصيلي
          </p>
        </div>
        <div className="px-2 py-2 md:px-2.5 md:py-2.5">
          <ChartContainer height={320}>
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 8, right: 12, left: 4, bottom: 4 }}
            >
              <CartesianGrid stroke={chartTheme.grid} horizontal={false} />
              <XAxis
                type="number"
                tick={{ fill: chartTheme.text, fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${(v / 1_000_000).toFixed(1)}M`}
              />
              <YAxis
                type="category"
                dataKey="department"
                width={120}
                tick={{ fill: chartTheme.text, fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Bar
                dataKey="amount"
                fill={chartTheme.primary}
                radius={[0, 6, 6, 0]}
                barSize={20}
                name="الهدر"
              />
            </BarChart>
          </ChartContainer>
        </div>
      </article>
    </Link>
  );
}
