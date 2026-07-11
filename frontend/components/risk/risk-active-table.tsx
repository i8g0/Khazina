"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import type { RiskItem } from "@/lib/placeholder-data";
import { riskItems } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("ar-SA", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function priorityBadgeVariant(priority: string) {
  if (priority === "عالية") {
    return "destructive" as const;
  }
  if (priority === "متوسطة") {
    return "warning" as const;
  }
  return "secondary" as const;
}

function statusBadgeVariant(status: string) {
  if (status === "قيد المعالجة") {
    return "warning" as const;
  }
  return "outline" as const;
}

const columns: DataTableColumn<RiskItem>[] = [
  {
    key: "name",
    header: "الخطر",
    className: "px-7 py-6 min-w-[200px]",
    cell: (row) => (
      <div className="space-y-1">
        <p className="text-[15px] font-semibold text-black-primary">{row.name}</p>
        <p className="text-xs text-muted">{row.description}</p>
      </div>
    ),
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
    key: "priority",
    header: "الأولوية",
    className: "px-7 py-6",
    cell: (row) => (
      <Badge
        variant={priorityBadgeVariant(row.priority)}
        className="px-3 py-1.5 text-xs font-semibold"
      >
        {row.priority}
      </Badge>
    ),
  },
  {
    key: "status",
    header: "الحالة",
    className: "px-7 py-6",
    cell: (row) => (
      <Badge
        variant={statusBadgeVariant(row.status)}
        className="px-3 py-1.5 text-xs font-semibold"
      >
        {row.status}
      </Badge>
    ),
  },
  {
    key: "owner",
    header: "المسؤول",
    className: "px-7 py-6 text-sm text-gray-medium",
    cell: (row) => row.owner,
  },
  {
    key: "lastUpdated",
    header: "آخر تحديث",
    className: "px-7 py-6 text-sm tabular-nums text-muted",
    cell: (row) => formatDate(row.lastUpdated),
  },
];

export interface RiskActiveTableProps {
  className?: string;
}

export function RiskActiveTable({ className }: RiskActiveTableProps) {
  return (
    <DataTable
      columns={columns}
      data={riskItems}
      className={cn(
        "rounded-2xl border-border/60 shadow-none",
        className,
      )}
    />
  );
}
