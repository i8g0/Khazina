"use client";

import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import type { RiskAnalysisHistoryItem } from "@/lib/risk/view-types";
import { cn } from "@/lib/utils";

const columns: DataTableColumn<RiskAnalysisHistoryItem>[] = [
  {
    key: "title",
    header: "التحليل",
    className: "px-6 py-4",
    cell: (row) => (
      <span className="text-sm font-semibold text-black-primary">{row.title}</span>
    ),
  },
  {
    key: "date",
    header: "التاريخ",
    className: "px-6 py-4 text-sm text-muted",
    cell: (row) => row.date,
  },
  {
    key: "findings",
    header: "النتائج",
    className: "px-6 py-4 tabular-nums text-sm",
    cell: (row) => row.findings,
  },
  {
    key: "posture",
    header: "الوضع العام",
    className: "px-6 py-4 text-sm",
    cell: (row) => row.posture,
  },
  {
    key: "status",
    header: "الحالة",
    className: "px-6 py-4 text-sm text-muted",
    cell: (row) => row.status,
  },
];

export interface RiskAnalysesTableProps {
  data: RiskAnalysisHistoryItem[];
  className?: string;
}

export function RiskAnalysesTable({ data, className }: RiskAnalysesTableProps) {
  return (
    <DataTable
      columns={columns}
      data={data}
      className={cn("rounded-2xl border-border/60 shadow-none", className)}
    />
  );
}
