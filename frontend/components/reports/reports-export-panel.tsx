"use client";

import * as React from "react";
import { FileSpreadsheet, FileText, Presentation } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { reportExportFormats } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

const iconMap = {
  pdf: FileText,
  excel: FileSpreadsheet,
  pptx: Presentation,
} as const;

export interface ReportsExportPanelProps {
  className?: string;
  onPdfExport?: () => void;
  pdfExporting?: boolean;
  pdfEnabled?: boolean;
}

export function ReportsExportPanel({
  className,
  onPdfExport,
  pdfExporting = false,
  pdfEnabled = false,
}: ReportsExportPanelProps) {
  return (
    <article
      className={cn(
        "rounded-2xl border border-border/60 bg-surface px-6 py-5 md:px-6 md:py-6",
        className,
      )}
    >
      <div className="mb-6 space-y-2">
        <h3 className="text-xl font-semibold tracking-tight text-black-primary md:text-[1.35rem]">
          خيارات التصدير
        </h3>
        <p className="text-sm leading-relaxed text-muted md:text-[15px]">
          تصدير التقارير بصيغ مختلفة — PDF متاح للتجربة التنفيذية
        </p>
      </div>
      <div className="flex flex-wrap gap-4">
        {reportExportFormats.map((format) => {
          const Icon = iconMap[format.icon];
          const isPdf = format.id === "pdf";
          if (isPdf) {
            return (
              <Button
                key={format.id}
                variant="secondary"
                disabled={!pdfEnabled || pdfExporting}
                onClick={onPdfExport}
              >
                <Icon className="h-4 w-4" strokeWidth={1.75} />
                {pdfExporting ? "جاري التصدير..." : format.label}
              </Button>
            );
          }
          return (
            <Tooltip key={format.id}>
              <TooltipTrigger asChild>
                <span className="inline-flex">
                  <Button variant="secondary" disabled>
                    <Icon className="h-4 w-4" strokeWidth={1.75} />
                    {format.label}
                  </Button>
                </span>
              </TooltipTrigger>
              <TooltipContent>قريباً</TooltipContent>
            </Tooltip>
          );
        })}
      </div>
    </article>
  );
}
