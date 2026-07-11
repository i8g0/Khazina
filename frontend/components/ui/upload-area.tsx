"use client";

import * as React from "react";
import { Upload } from "lucide-react";
import { cn } from "@/lib/utils";

export interface UploadAreaProps {
  title?: string;
  description?: string;
  accept?: string;
  multiple?: boolean;
  disabled?: boolean;
  onFilesSelected?: (files: FileList) => void;
  className?: string;
}

export function UploadArea({
  title = "اسحب الملفات هنا أو انقر للاختيار",
  description = "يدعم الملفات المعتمدة حسب إعدادات النظام",
  accept,
  multiple = false,
  disabled = false,
  onFilesSelected,
  className,
}: UploadAreaProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = React.useState(false);

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0 || disabled) return;
    onFilesSelected?.(files);
  };

  return (
    <div
      className={cn(
        "relative flex min-h-[180px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-border bg-surface px-6 py-10 text-center shadow-soft transition-all",
        isDragging && "border-gold-primary bg-gold-primary/5",
        !disabled && "hover:border-gold-primary/40 hover:bg-bg-light",
        disabled && "cursor-not-allowed opacity-60",
        className,
      )}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        handleFiles(event.dataTransfer.files);
      }}
      role="button"
      tabIndex={disabled ? -1 : 0}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          inputRef.current?.click();
        }
      }}
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept={accept}
        multiple={multiple}
        disabled={disabled}
        onChange={(event) => handleFiles(event.target.files)}
      />
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gold-primary/10 text-gold-primary">
        <Upload className="h-5 w-5" />
      </div>
      <p className="text-sm font-medium text-black-primary">{title}</p>
      <p className="mt-2 max-w-md text-xs text-muted">{description}</p>
    </div>
  );
}
