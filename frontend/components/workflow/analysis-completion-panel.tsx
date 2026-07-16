"use client";

import Link from "next/link";
import { CheckCircle2, Download, FileText, Home, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { navRouteMap } from "@/lib/app-nav";

export interface AnalysisCompletionPanelProps {
  onViewReport?: () => void;
  onExportPdf?: () => void;
  pdfExporting?: boolean;
  className?: string;
}

export function AnalysisCompletionPanel({
  onViewReport,
  onExportPdf,
  pdfExporting = false,
  className,
}: AnalysisCompletionPanelProps) {
  return (
    <section
      className={cn(
        "rounded-2xl border border-gold-primary/30 bg-gold-primary/[0.06] px-6 py-6 md:px-8 md:py-7",
        className,
      )}
    >
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex gap-4">
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gold-primary text-white">
            <CheckCircle2 className="h-6 w-6" strokeWidth={1.75} />
          </span>
          <div className="space-y-1.5">
            <h2 className="text-xl font-semibold text-black-primary">
              اكتمل التحليل بنجاح
            </h2>
            <p className="max-w-xl text-sm leading-relaxed text-gray-medium md:text-[15px]">
              تم إنشاء التقرير التنفيذي. يمكنك مراجعته أو تصديره بصيغة PDF، أو
              بدء تحليل لمجموعة بيانات جديدة.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          {onViewReport ? (
            <Button variant="secondary" onClick={onViewReport}>
              <FileText className="h-4 w-4" />
              عرض التقرير التنفيذي
            </Button>
          ) : null}
          {onExportPdf ? (
            <Button disabled={pdfExporting} onClick={onExportPdf}>
              <Download className="h-4 w-4" />
              {pdfExporting ? "جاري التصدير..." : "تصدير PDF"}
            </Button>
          ) : null}
          <Button asChild variant="secondary">
            <Link href={navRouteMap.data}>
              <Upload className="h-4 w-4" />
              تحليل مجموعة جديدة
            </Link>
          </Button>
          <Button asChild variant="ghost">
            <Link href={navRouteMap.dashboard}>
              <Home className="h-4 w-4" />
              العودة إلى لوحة التحكم
            </Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
