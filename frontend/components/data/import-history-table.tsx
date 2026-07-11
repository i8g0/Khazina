"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import type { ImportHistoryItem } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("ar-SA", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function statusVariant(status: string) {
  if (status === "نجح") {
    return "success" as const;
  }
  if (status.includes("قيد")) {
    return "warning" as const;
  }
  if (status.includes("فشل")) {
    return "destructive" as const;
  }
  return "secondary" as const;
}

const columns: DataTableColumn<ImportHistoryItem>[] = [
  {
    key: "date",
    header: "التاريخ",
    className: "px-7 py-6 text-sm tabular-nums text-muted",
    cell: (row) => formatDate(row.date),
  },
  {
    key: "file",
    header: "الملف",
    className: "px-7 py-6 text-[15px] font-semibold",
    cell: (row) => row.file,
  },
  {
    key: "records",
    header: "السجلات",
    className: "px-7 py-6 text-sm tabular-nums text-gray-medium",
    cell: (row) => row.records,
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

export interface ImportHistoryTableProps {
  items: ImportHistoryItem[];
  className?: string;
}

export function ImportHistoryTable({ items, className }: ImportHistoryTableProps) {
  return (
    <DataTable
      columns={columns}
      data={items}
      emptyMessage="لا يوجد سجل استيراد"
      className={cn("rounded-2xl border-border/60 shadow-none", className)}
    />
  );
}
