"use client";

import * as React from "react";
import { Upload } from "lucide-react";
import { UploadArea } from "@/components/ui/upload-area";
import { cn } from "@/lib/utils";

export interface UploadDataPanelProps {
  disabled?: boolean;
  onUpload: (fileName: string) => void;
  className?: string;
}

export function UploadDataPanel({
  disabled = false,
  onUpload,
  className,
}: UploadDataPanelProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);

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
      <div className="mt-4 flex flex-wrap gap-2">
        {["Excel", "CSV", "تحقق تلقائي"].map((badge) => (
          <span
            key={badge}
            className="inline-flex items-center gap-1.5 rounded-full border border-border/70 bg-bg-light px-3 py-1 text-xs font-medium text-gray-medium"
          >
            <Upload className="h-3 w-3" strokeWidth={1.75} />
            {badge}
          </span>
        ))}
      </div>
    </section>
  );
}
