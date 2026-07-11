"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import type { UploadedFileItem } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("ar-SA", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function statusVariant(status: string) {
  if (status === "مكتمل") {
    return "success" as const;
  }
  if (status === "قيد المعالجة") {
    return "warning" as const;
  }
  if (status === "فشل") {
    return "destructive" as const;
  }
  return "secondary" as const;
}

const columns: DataTableColumn<UploadedFileItem>[] = [
  {
    key: "fileName",
    header: "اسم الملف",
    className: "px-7 py-6 min-w-[200px] text-[15px] font-semibold",
    cell: (row) => row.fileName,
  },
  {
    key: "department",
    header: "القسم",
    className: "px-7 py-6",
    cell: (row) => (
      <span className="rounded-full border border-border/70 bg-bg-light px-3 py-1 text-xs font-medium text-gray-medium">
        {row.department}
      </span>
    ),
  },
  {
    key: "uploadDate",
    header: "تاريخ الرفع",
    className: "px-7 py-6 text-sm tabular-nums text-muted",
    cell: (row) => formatDate(row.uploadDate),
  },
  {
    key: "size",
    header: "الحجم",
    className: "px-7 py-6 text-sm tabular-nums text-gray-medium",
    cell: (row) => row.size,
  },
  {
    key: "status",
    header: "الحالة",
    className: "px-7 py-6",
    cell: (row) => (
      <Badge
        variant={statusVariant(row.status)}
        className="px-3 py-1.5 text-xs font-semibold"
      >
        {row.status}
      </Badge>
    ),
  },
];

export interface UploadedFilesTableProps {
  files: UploadedFileItem[];
  className?: string;
}

export function UploadedFilesTable({ files, className }: UploadedFilesTableProps) {
  return (
    <DataTable
      columns={columns}
      data={files}
      emptyMessage="لا توجد ملفات"
      className={cn("rounded-2xl border-border/60 shadow-none", className)}
    />
  );
}
