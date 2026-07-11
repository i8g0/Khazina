"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import type { SimulationImpactItem } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

function changeVariant(direction: SimulationImpactItem["direction"]) {
  if (direction === "up") {
    return "warning" as const;
  }
  if (direction === "down") {
    return "success" as const;
  }
  return "secondary" as const;
}

const columns: DataTableColumn<SimulationImpactItem>[] = [
  {
    key: "category",
    header: "الفئة",
    className: "px-7 py-6 text-[15px] font-semibold",
    cell: (row) => row.category,
  },
  {
    key: "baseline",
    header: "الأساس",
    className: "px-7 py-6 tabular-nums",
    cell: (row) => row.baseline,
  },
  {
    key: "projected",
    header: "المتوقع",
    className: "px-7 py-6 tabular-nums",
    cell: (row) => row.projected,
  },
  {
    key: "change",
    header: "التغير",
    className: "px-7 py-6",
    cell: (row) => (
      <Badge
        variant={changeVariant(row.direction)}
        className="px-3 py-1 text-xs font-semibold"
      >
        {row.change}
      </Badge>
    ),
  },
];

export interface SimulationImpactBreakdownProps {
  items: SimulationImpactItem[];
  className?: string;
}

export function SimulationImpactBreakdown({
  items,
  className,
}: SimulationImpactBreakdownProps) {
  return (
    <DataTable
      columns={columns}
      data={items}
      className={cn("rounded-2xl border-border/60 shadow-none", className)}
    />
  );
}
