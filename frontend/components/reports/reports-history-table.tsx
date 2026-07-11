"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import type { ReportItem } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("ar-SA", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function statusVariant(status: string) {
  if (status === "جاهز") {
    return "success" as const;
  }
  if (status === "مسودة") {
    return "warning" as const;
  }
  return "secondary" as const;
}

const columns: DataTableColumn<ReportItem>[] = [
  {
    key: "title",
    header: "التقرير",
    className: "px-6 py-4 min-w-[220px] text-[15px] font-semibold",
    cell: (row) => row.title,
  },
  {
    key: "type",
    header: "النوع",
    className: "px-6 py-4",
    cell: (row) => (
      <span className="rounded-full border border-border/70 bg-bg-light px-3 py-1 text-xs font-medium text-gray-medium">
        {row.type}
      </span>
    ),
  },
  {
    key: "department",
    header: "القسم",
    className: "px-6 py-4 text-sm text-gray-medium",
    cell: (row) => row.department,
  },
  {
    key: "sourceFile",
    header: "ملف المصدر",
    className: "px-6 py-4 text-sm text-muted",
    cell: (row) => row.sourceFile,
  },
  {
    key: "date",
    header: "التاريخ",
    className: "px-6 py-4 text-sm tabular-nums text-muted",
    cell: (row) => formatDate(row.date),
  },
  {
    key: "status",
    header: "الحالة",
    className: "px-6 py-4",
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

export interface ReportsHistoryTableProps {
  reports: ReportItem[];
  className?: string;
}

export function ReportsHistoryTable({ reports, className }: ReportsHistoryTableProps) {
  return (
    <DataTable
      columns={columns}
      data={reports}
      emptyMessage="لا توجد تقارير"
      className={cn("rounded-2xl border-border/60 shadow-none", className)}
    />
  );
}
