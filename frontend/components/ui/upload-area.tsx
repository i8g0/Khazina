"use client";

import * as React from "react";
import { Upload } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export interface UploadAreaProps {
  title?: string;
  description?: string;
  accept?: string;
  multiple?: boolean;
  disabled?: boolean;
  onFilesSelected?: (files: FileList) => void;
  variant?: "default" | "prominent";
  actionLabel?: string;
  className?: string;
}

export function UploadArea({
  title = "اسحب الملفات هنا أو انقر للاختيار",
  description = "يدعم الملفات المعتمدة حسب إعدادات النظام",
  accept,
  multiple = false,
  disabled = false,
  onFilesSelected,
  variant = "default",
  actionLabel,
  className,
}: UploadAreaProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = React.useState(false);
  const isProminent = variant === "prominent";

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0 || disabled) return;
    onFilesSelected?.(files);
  };

  const openFilePicker = () => {
    if (!disabled) {
      inputRef.current?.click();
    }
  };

  return (
    <div
      className={cn(
        "relative flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed text-center transition-all",
        isProminent
          ? "min-h-[280px] border-gold-primary/25 bg-surface px-8 py-12 md:min-h-[320px] md:px-12 md:py-14"
          : "min-h-[180px] rounded-xl border-border bg-surface px-6 py-10 shadow-soft",
        isDragging && "border-gold-primary bg-gold-primary/5 shadow-none",
        !disabled &&
          (isProminent
            ? "hover:border-gold-primary/50 hover:bg-gold-primary/[0.04]"
            : "hover:border-gold-primary/40 hover:bg-bg-light"),
        disabled && "cursor-not-allowed opacity-60",
        className,
      )}
      onClick={openFilePicker}
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
          openFilePicker();
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
      <div
        className={cn(
          "mb-5 flex items-center justify-center rounded-2xl bg-gold-primary/10 text-gold-primary",
          isProminent ? "h-16 w-16" : "mb-4 h-12 w-12 rounded-full",
        )}
      >
        <Upload
          className={cn(isProminent ? "h-7 w-7" : "h-5 w-5")}
          strokeWidth={1.75}
        />
      </div>
      <p
        className={cn(
          "font-semibold text-black-primary",
          isProminent ? "text-lg md:text-xl" : "text-sm font-medium",
        )}
      >
        {title}
      </p>
      <p
        className={cn(
          "mt-2 max-w-lg text-muted",
          isProminent ? "text-sm leading-relaxed md:text-[15px]" : "text-xs",
        )}
      >
        {description}
      </p>
      {actionLabel ? (
        <Button
          type="button"
          variant="primary"
          size={isProminent ? "lg" : "md"}
          className="pointer-events-none mt-6"
          tabIndex={-1}
          aria-hidden="true"
        >
          {actionLabel}
        </Button>
      ) : null}
    </div>
  );
}

export type UploadAreaHandle = {
  openFilePicker: () => void;
};
