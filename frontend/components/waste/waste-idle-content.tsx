"use client";

import Link from "next/link";
import {
  ArrowDown,
  BarChart3,
  Check,
  Clock,
  FileSpreadsheet,
  Lightbulb,
  Lock,
  Upload,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { navRouteMap } from "@/lib/app-nav";
import { EXECUTIVE_MESSAGES } from "@/lib/workflow/messages";

const helperItems = [
  { label: "Excel", icon: FileSpreadsheet },
  { label: "CSV", icon: FileSpreadsheet },
  { label: "حتى 10MB", icon: Check },
  { label: "تحليل آمن", icon: Lock },
  { label: "نتائج خلال ثوانٍ", icon: Clock },
];

const workflowSteps = [
  { id: "upload", label: "رفع الملف", icon: Upload },
  { id: "analyze", label: "تحليل البيانات", icon: BarChart3 },
  { id: "detect", label: "كشف الهدر", icon: Lightbulb },
  { id: "recommend", label: "التوصيات", icon: Check },
];

export interface WasteIdleContentProps {
  onUploadClick: () => void;
  preferDataManagement?: boolean;
  className?: string;
}

export function WasteIdleContent({
  onUploadClick,
  preferDataManagement = false,
  className,
}: WasteIdleContentProps) {
  return (
    <div className={cn("space-y-5 md:space-y-6", className)}>
      <div className="flex flex-wrap gap-2.5 md:gap-3">
        {helperItems.map((item) => {
          const Icon = item.icon;
          return (
            <span
              key={item.label}
              className="inline-flex items-center gap-2 rounded-full border border-border/70 bg-surface px-3.5 py-2 text-xs font-medium text-gray-medium md:text-sm"
            >
              <Icon className="h-3.5 w-3.5 text-gold-dark" strokeWidth={1.75} />
              {item.label}
            </span>
          );
        })}
      </div>

      <section className="rounded-2xl border border-border/60 bg-surface px-5 py-5 md:px-7 md:py-6">
        <p className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-muted">
          كيف يعمل
        </p>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {workflowSteps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={step.id} className="relative flex items-start gap-3">
                {index < workflowSteps.length - 1 ? (
                  <span
                    aria-hidden="true"
                    className="absolute start-[15px] top-10 hidden h-px w-[calc(100%+0.75rem)] bg-border/70 xl:block"
                  />
                ) : null}
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gold-primary/10 text-gold-dark">
                  <Icon className="h-4 w-4" strokeWidth={1.75} />
                </span>
                <div className="min-w-0 pt-0.5">
                  <p className="text-[11px] font-medium text-muted">
                    {index + 1}
                  </p>
                  <p className="text-sm font-semibold text-black-primary">
                    {step.label}
                  </p>
                </div>
                {index < workflowSteps.length - 1 ? (
                  <ArrowDown
                    aria-hidden="true"
                    className="ms-auto mt-1 h-4 w-4 shrink-0 text-border xl:hidden"
                    strokeWidth={1.75}
                  />
                ) : null}
              </div>
            );
          })}
        </div>
      </section>

      <section className="rounded-2xl border border-border/60 bg-bg-light/40 px-6 py-6 text-center md:px-8 md:py-7">
        <div className="mx-auto flex max-w-xl flex-col items-center">
          <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gold-primary/10 text-gold-dark">
            <FileSpreadsheet className="h-6 w-6" strokeWidth={1.75} />
          </span>
          <h2 className="text-xl font-semibold tracking-tight text-black-primary md:text-[1.35rem]">
            {preferDataManagement
              ? "ارفع ملفك من مركز البيانات المالية أولاً"
              : "ابدأ بتحليل ملفاتك المالية"}
          </h2>
          <p className="mt-3 text-sm leading-7 text-muted md:text-[15px]">
            {preferDataManagement
              ? EXECUTIVE_MESSAGES.uploadPrimaryHint
              : "ارفع ملف Excel أو CSV لاكتشاف أنماط الهدر المالي وفرص التوفير المؤسسية. ستظهر النتائج هنا بعد اكتمال التحليل."}
          </p>
          {preferDataManagement ? (
            <Button asChild type="button" variant="primary" size="lg" className="mt-6">
              <Link href={navRouteMap.data}>
                <Upload className="h-4 w-4" strokeWidth={1.75} />
                الانتقال إلى مركز البيانات المالية
              </Link>
            </Button>
          ) : (
            <Button
              type="button"
              variant="primary"
              size="lg"
              className="mt-6"
              onClick={onUploadClick}
            >
              <Upload className="h-4 w-4" strokeWidth={1.75} />
              رفع مباشر وتحليل
            </Button>
          )}
          <p className="mt-4 text-xs text-muted">
            {preferDataManagement
              ? EXECUTIVE_MESSAGES.uploadQuickHint
              : "أو ارفع من مركز البيانات المالية — الطريقة الموصى بها للمستخدمين الجدد."}
          </p>
        </div>
      </section>
    </div>
  );
}
