"use client";

import { BarChart3, LineChart as LineChartIcon } from "lucide-react";
import { EmptyState } from "@/components/ui/empty-state";
import { cn } from "@/lib/utils";
import { EXECUTIVE_MESSAGES } from "@/lib/workflow/messages";

interface DashboardChartCardProps {
  title: string;
  description: string;
  emptyTitle: string;
  emptyDescription: string;
  icon: React.ReactNode;
  height?: number;
}

function DashboardChartCard({
  title,
  description,
  emptyTitle,
  emptyDescription,
  icon,
  height = 360,
}: DashboardChartCardProps) {
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
            "flex w-full items-center justify-center overflow-hidden rounded-xl bg-bg-light/30 px-1 py-1.5",
          )}
          style={{ minHeight: height }}
        >
          <EmptyState
            title={emptyTitle}
            description={emptyDescription}
            icon={icon}
            className="w-full border-none bg-transparent shadow-none"
          />
        </div>
      </div>
    </article>
  );
}

export function DashboardCharts() {
  return (
    <div className="grid gap-5 xl:grid-cols-2 xl:gap-6">
      <DashboardChartCard
        title="توزيع الهدر حسب الإدارات"
        description="تحديد الإدارات الأعلى مساهمة في الهدر المالي"
        emptyTitle="لا يتوفر رسم بياني للإدارات"
        emptyDescription={EXECUTIVE_MESSAGES.chartDepartmentEmpty}
        icon={<BarChart3 className="h-6 w-6" />}
        height={360}
      />
      <DashboardChartCard
        title="اتجاه الهدر المالي"
        description="تطور الهدر المكتشف خلال الفترات السابقة"
        emptyTitle="لا يتوفر رسم اتجاه الهدر"
        emptyDescription={EXECUTIVE_MESSAGES.chartTrendEmpty}
        icon={<LineChartIcon className="h-6 w-6" />}
        height={360}
      />
    </div>
  );
}
