"use client";

import * as React from "react";
import { Download, Eye, FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Modal,
  ModalContent,
  ModalDescription,
  ModalHeader,
  ModalTitle,
} from "@/components/ui/modal";
import type { ReportItem } from "@/lib/placeholder-data";
import { formatDate } from "@/lib/format";
import { cn } from "@/lib/utils";

function statusVariant(status: string) {
  if (status === "جاهز") {
    return "success" as const;
  }
  if (status === "مسودة") {
    return "warning" as const;
  }
  return "secondary" as const;
}

export interface ReportsCardProps {
  report: ReportItem;
  selected?: boolean;
  onSelect?: () => void;
  onExportPdf?: () => void;
  pdfExporting?: boolean;
  className?: string;
}

export function ReportsCard({
  report,
  selected = false,
  onSelect,
  onExportPdf,
  pdfExporting = false,
  className,
}: ReportsCardProps) {
  const [previewOpen, setPreviewOpen] = React.useState(false);
  const canExport = Boolean(report.hasContent);

  return (
    <>
      <article
        className={cn(
          "flex h-full flex-col rounded-2xl border bg-surface px-5 py-5 transition-colors md:px-6 md:py-5",
          selected
            ? "border-gold-primary ring-2 ring-gold-primary/20"
            : "border-border/60 hover:border-gold-primary/25",
          className,
        )}
      >
        <button
          type="button"
          className="flex flex-1 flex-col text-right"
          onClick={onSelect}
        >
          <div className="mb-3 flex items-start justify-between gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gold-primary/10 text-gold-dark">
              <FileText className="h-[18px] w-[18px]" strokeWidth={1.75} />
            </span>
            <Badge
              variant={statusVariant(report.status)}
              className="px-3 py-1 text-xs font-semibold"
            >
              {report.status}
            </Badge>
          </div>

          <Badge variant="outline" className="mb-3 w-fit px-3 py-1 text-xs font-semibold">
            {report.type}
          </Badge>

          <h3 className="mb-2 text-base font-semibold leading-snug tracking-tight text-black-primary md:text-lg">
            {report.title}
          </h3>

          <div className="mb-3 flex flex-wrap gap-2 text-xs text-muted">
            <span className="rounded-full border border-border/70 bg-bg-light px-3 py-1 font-medium text-gray-medium">
              {report.department}
            </span>
            <span className="rounded-full border border-border/70 bg-bg-light px-3 py-1 font-medium tabular-nums text-gray-medium">
              {formatDate(report.date)}
            </span>
          </div>

          <p className="mb-2 text-xs font-medium text-muted">المصدر: {report.sourceFile}</p>
        </button>

        <div className="mt-auto grid gap-2 border-t border-border/60 pt-4 sm:grid-cols-2">
          <Button
            variant="secondary"
            className="w-full"
            onClick={() => setPreviewOpen(true)}
          >
            <Eye className="h-4 w-4" strokeWidth={1.75} />
            معاينة
          </Button>
          <Button
            variant="secondary"
            className="w-full"
            disabled={!canExport || pdfExporting}
            onClick={onExportPdf}
          >
            <Download className="h-4 w-4" strokeWidth={1.75} />
            {pdfExporting ? "جاري التصدير..." : "PDF"}
          </Button>
        </div>
      </article>

      <Modal open={previewOpen} onOpenChange={setPreviewOpen}>
        <ModalContent className="max-w-2xl">
          <ModalHeader>
            <ModalTitle>{report.title}</ModalTitle>
            <ModalDescription>
              {report.type} · {report.department} · {formatDate(report.date)}
            </ModalDescription>
          </ModalHeader>
          <div className="space-y-4 text-sm leading-7 text-muted">
            <p>{report.previewText}</p>
          </div>
        </ModalContent>
      </Modal>
    </>
  );
}
