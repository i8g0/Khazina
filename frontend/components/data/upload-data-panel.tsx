"use client";

import * as React from "react";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { UploadArea } from "@/components/ui/upload-area";
import { cn } from "@/lib/utils";

export interface UploadDataPanelProps {
  disabled?: boolean;
  compact?: boolean;
  onUpload: (fileName: string) => void;
  className?: string;
}

export function UploadDataPanel({
  disabled = false,
  compact = false,
  onUpload,
  className,
}: UploadDataPanelProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);

  if (compact) {
    return (
      <article
        className={cn(
          "flex flex-col gap-4 rounded-2xl border border-border/60 bg-surface px-6 py-5 md:flex-row md:items-center md:justify-between md:px-7 md:py-6",
          className,
        )}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".xlsx,.xls,.csv"
          disabled={disabled}
          onChange={(event) => {
            const file = event.target.files?.[0];
            onUpload(file?.name ?? "Dataset.xlsx");
          }}
        />
        <div className="space-y-1">
          <p className="text-sm font-semibold text-black-primary">رفع ملف إلى المستودع</p>
          <p className="text-xs text-muted">.xlsx · .xls · .csv — حتى 10 ميغابايت</p>
        </div>
        <Button
          variant="secondary"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
        >
          <Upload className="h-4 w-4" strokeWidth={1.75} />
          اختيار ملف
        </Button>
      </article>
    );
  }

  return (
    <section className={cn("relative", className)}>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept=".xlsx,.xls,.csv"
        disabled={disabled}
        onChange={(event) => {
          const file = event.target.files?.[0];
          onUpload(file?.name ?? "Dataset.xlsx");
        }}
      />
      <UploadArea
        variant="prominent"
        title="رفع مجموعة بيانات مالية"
        description="يدعم .xlsx و .xls و .csv — حتى 10 ميغابايت"
        accept=".xlsx,.xls,.csv"
        actionLabel="اختيار ملف للرفع"
        disabled={disabled}
        onFilesSelected={(files) => {
          onUpload(files[0]?.name ?? "Dataset.xlsx");
        }}
      />
    </section>
  );
}
