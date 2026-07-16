"use client";

import { Bar, BarChart, CartesianGrid, Cell, XAxis, YAxis } from "recharts";
import { ChartContainer, chartTheme } from "@/components/ui/chart-container";
import type {
  RiskCategoryChartItem,
  RiskDepartmentChartItem,
  RiskExposureChartItem,
  RiskSeverityChartItem,
  RiskTopItemChart,
  RiskTrendChartItem,
} from "@/lib/risk/view-types";
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
      <div className="space-y-1 border-b border-border/60 px-5 py-3.5">
        <h3 className="text-base font-semibold tracking-tight text-black-primary md:text-[1.1rem]">
          {title}
        </h3>
        <p className="text-sm leading-relaxed text-muted">{description}</p>
      </div>
      <div className="px-2 py-2 md:px-2.5 md:py-2.5">
        <div
          className={cn(
            "w-full overflow-hidden rounded-xl bg-bg-light/30 px-1 py-1.5",
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

export interface RiskChartsProps {
  byDepartment: RiskDepartmentChartItem[];
  bySeverity: RiskSeverityChartItem[];
  byCategory?: RiskCategoryChartItem[];
  exposureByDepartment?: RiskExposureChartItem[];
  exposureBySupplier?: RiskExposureChartItem[];
  wasteByDepartment?: RiskExposureChartItem[];
  potentialSavings?: RiskExposureChartItem[];
  topRisks?: RiskTopItemChart[];
  riskTrend?: RiskTrendChartItem[];
}

export function RiskCharts({
  byDepartment,
  bySeverity,
  byCategory = [],
  exposureByDepartment = [],
  exposureBySupplier = [],
  wasteByDepartment = [],
  potentialSavings = [],
  topRisks = [],
  riskTrend = [],
}: RiskChartsProps) {
  return (
    <div className="grid gap-5 xl:grid-cols-2 xl:gap-6">
      {byDepartment.length > 0 ? (
        <RiskChartCard
          title="أخطر الإدارات"
          description="متوسط درجة المخاطر حسب الإدارة من التحليل الحالي"
          height={360}
        >
          <ChartContainer height={360}>
            <BarChart
              data={byDepartment}
              layout="vertical"
              margin={{ top: 8, right: 12, left: 4, bottom: 4 }}
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
      ) : null}

      <RiskChartCard
        title="توزيع المخاطر حسب الأولوية"
        description="عدد النتائج — أين يركز الانتباه التنفيذي"
        height={360}
      >
        <ChartContainer height={360}>
          <BarChart data={bySeverity} margin={{ top: 8, right: 12, left: 4, bottom: 4 }}>
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
              {bySeverity.map((entry) => (
                <Cell
                  key={entry.level}
                  fill={severityColors[entry.level] ?? chartTheme.primary}
                />
              ))}
            </Bar>
          </BarChart>
        </ChartContainer>
      </RiskChartCard>

      {wasteByDepartment.length > 0 ? (
        <RiskChartCard
          title="الهدر حسب الإدارة"
          description="أين يتركّز الهدر المالي — من بيانات التحليل المرفوعة"
          height={360}
        >
          <ChartContainer height={360}>
            <BarChart
              data={wasteByDepartment}
              layout="vertical"
              margin={{ top: 8, right: 12, left: 4, bottom: 4 }}
            >
              <CartesianGrid stroke={chartTheme.grid} horizontal={false} />
              <XAxis type="number" tick={{ fill: chartTheme.text, fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="label"
                width={120}
                tick={{ fill: chartTheme.text, fontSize: 10 }}
              />
              <Bar dataKey="amount" fill="#5D4037" radius={[0, 6, 6, 0]} barSize={20} name="قيمة الهدر" />
            </BarChart>
          </ChartContainer>
        </RiskChartCard>
      ) : null}

      {riskTrend.length > 1 ? (
        <RiskChartCard
          title="اتجاه المخاطر"
          description="تطوّر عدد المخاطر المكتشفة عبر التحليلات"
          height={360}
        >
          <ChartContainer height={360}>
            <BarChart data={riskTrend} margin={{ top: 8, right: 12, left: 4, bottom: 4 }}>
              <CartesianGrid stroke={chartTheme.grid} vertical={false} />
              <XAxis
                dataKey="label"
                tick={{ fill: chartTheme.text, fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis allowDecimals={false} tick={{ fill: chartTheme.text, fontSize: 12 }} />
              <Bar dataKey="findings" fill={chartTheme.primary} radius={[6, 6, 0, 0]} barSize={36} name="عدد المخاطر" />
            </BarChart>
          </ChartContainer>
        </RiskChartCard>
      ) : null}

      {exposureByDepartment.length > 0 ? (
        <RiskChartCard
          title="التعرّض المالي حسب الإدارة"
          description="إجمالي المبالغ المعرّضة (ر.س) — من بيانات التحليل"
          height={360}
        >
          <ChartContainer height={360}>
            <BarChart
              data={exposureByDepartment}
              layout="vertical"
              margin={{ top: 8, right: 12, left: 4, bottom: 4 }}
            >
              <CartesianGrid stroke={chartTheme.grid} horizontal={false} />
              <XAxis type="number" tick={{ fill: chartTheme.text, fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="label"
                width={120}
                tick={{ fill: chartTheme.text, fontSize: 10 }}
              />
              <Bar dataKey="amount" fill="#8B6914" radius={[0, 6, 6, 0]} barSize={20} />
            </BarChart>
          </ChartContainer>
        </RiskChartCard>
      ) : null}

      {exposureBySupplier.length > 0 ? (
        <RiskChartCard
          title="أخطر الموردين"
          description="تركّز التعرّض المالي على الموردين"
          height={360}
        >
          <ChartContainer height={360}>
            <BarChart
              data={exposureBySupplier}
              layout="vertical"
              margin={{ top: 8, right: 12, left: 4, bottom: 4 }}
            >
              <CartesianGrid stroke={chartTheme.grid} horizontal={false} />
              <XAxis type="number" tick={{ fill: chartTheme.text, fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="label"
                width={120}
                tick={{ fill: chartTheme.text, fontSize: 10 }}
              />
              <Bar dataKey="amount" fill="#C0392B" radius={[0, 6, 6, 0]} barSize={20} />
            </BarChart>
          </ChartContainer>
        </RiskChartCard>
      ) : null}

      {byCategory.length > 0 ? (
        <RiskChartCard
          title="المخاطر حسب الفئة"
          description="متوسط درجة النتائج لكل فئة"
          height={360}
        >
          <ChartContainer height={360}>
            <BarChart data={byCategory} margin={{ top: 8, right: 12, left: 4, bottom: 4 }}>
              <CartesianGrid stroke={chartTheme.grid} vertical={false} />
              <XAxis
                dataKey="category"
                tick={{ fill: chartTheme.text, fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis domain={[0, 100]} tick={{ fill: chartTheme.text, fontSize: 12 }} />
              <Bar dataKey="score" fill={chartTheme.primary} radius={[6, 6, 0, 0]} barSize={40} />
            </BarChart>
          </ChartContainer>
        </RiskChartCard>
      ) : null}

      {potentialSavings.length > 0 ? (
        <RiskChartCard
          title="التوفير المحتمل"
          description="أعلى فرص التوفير من المعالجة"
          height={360}
        >
          <ChartContainer height={360}>
            <BarChart
              data={potentialSavings}
              layout="vertical"
              margin={{ top: 8, right: 12, left: 4, bottom: 4 }}
            >
              <CartesianGrid stroke={chartTheme.grid} horizontal={false} />
              <XAxis type="number" tick={{ fill: chartTheme.text, fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="label"
                width={140}
                tick={{ fill: chartTheme.text, fontSize: 9 }}
              />
              <Bar dataKey="amount" fill="#27AE60" radius={[0, 6, 6, 0]} barSize={18} />
            </BarChart>
          </ChartContainer>
        </RiskChartCard>
      ) : null}

      {topRisks.length > 0 ? (
        <RiskChartCard
          title="أهم 10 مخاطر"
          description="أعلى درجات الخطورة — للمتابعة الفورية"
          height={360}
        >
          <ChartContainer height={360}>
            <BarChart
              data={topRisks}
              layout="vertical"
              margin={{ top: 8, right: 12, left: 4, bottom: 4 }}
            >
              <CartesianGrid stroke={chartTheme.grid} horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tick={{ fill: chartTheme.text, fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="name"
                width={140}
                tick={{ fill: chartTheme.text, fontSize: 9 }}
              />
              <Bar dataKey="score" fill={chartTheme.primary} radius={[0, 6, 6, 0]} barSize={18} />
            </BarChart>
          </ChartContainer>
        </RiskChartCard>
      ) : null}
    </div>
  );
}
