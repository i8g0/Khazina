"use client";

import * as React from "react";
import { Eye, FileText } from "lucide-react";
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
  className?: string;
}

export function ReportsCard({ report, className }: ReportsCardProps) {
  const [previewOpen, setPreviewOpen] = React.useState(false);

  return (
    <>
      <article
        className={cn(
          "flex h-full flex-col rounded-2xl border border-border/60 bg-surface px-7 py-7 transition-colors hover:border-gold-primary/25 md:px-8 md:py-8",
          className,
        )}
      >
        <div className="mb-5 flex items-start justify-between gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gold-primary/10 text-gold-dark">
            <FileText className="h-[18px] w-[18px]" strokeWidth={1.75} />
          </span>
          <Badge
            variant={statusVariant(report.status)}
            className="px-3 py-1 text-xs font-semibold"
          >
            {report.status}
          </Badge>
        </div>

        <Badge variant="outline" className="mb-4 w-fit px-3 py-1 text-xs font-semibold">
          {report.type}
        </Badge>

        <h3 className="mb-2 text-lg font-semibold leading-snug tracking-tight text-black-primary md:text-xl">
          {report.title}
        </h3>

        <div className="mb-5 flex flex-wrap gap-2 text-xs text-muted">
          <span className="rounded-full border border-border/70 bg-bg-light px-3 py-1 font-medium text-gray-medium">
            {report.department}
          </span>
          <span className="rounded-full border border-border/70 bg-bg-light px-3 py-1 font-medium tabular-nums text-gray-medium">
            {report.date}
          </span>
        </div>

        <p className="mb-2 text-xs font-medium text-muted">المصدر: {report.sourceFile}</p>

        <div className="mt-auto border-t border-border/60 pt-5">
          <Button
            variant="secondary"
            className="w-full"
            onClick={() => setPreviewOpen(true)}
          >
            <Eye className="h-4 w-4" strokeWidth={1.75} />
            معاينة
          </Button>
        </div>
      </article>

      <Modal open={previewOpen} onOpenChange={setPreviewOpen}>
        <ModalContent className="max-w-2xl">
          <ModalHeader>
            <ModalTitle>{report.title}</ModalTitle>
            <ModalDescription>
              {report.type} · {report.department} · {report.date}
            </ModalDescription>
          </ModalHeader>
          <div className="space-y-4 text-sm leading-7 text-muted">
            <p>{report.previewText}</p>
            <p className="rounded-xl border border-border/60 bg-bg-light/50 px-5 py-4 text-xs text-gray-medium">
              معاينة تجريبية — التصدير الكامل متاح لاحقاً عبر خيارات التصدير.
            </p>
          </div>
        </ModalContent>
      </Modal>
    </>
  );
}
