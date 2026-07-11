"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { WasteAnalysisRow, WasteVendorDetail } from "@/lib/placeholder-data";

function formatAmount(value: number) {
  return value.toLocaleString("ar-SA");
}

export interface WasteBreakdownTableProps {
  analysisRows: WasteAnalysisRow[];
  vendorRows: WasteVendorDetail[];
  className?: string;
}

export function WasteBreakdownTable({
  analysisRows,
  vendorRows,
  className,
}: WasteBreakdownTableProps) {
  return (
    <div className={cn("space-y-8", className)}>
      <div className="overflow-hidden rounded-2xl border border-border/60 bg-surface">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse">
            <thead>
              <tr className="border-b border-border/70 bg-bg-light/50">
                {["الفئة", "المبلغ (ر.س)", "النسبة", "الإدارة"].map((header) => (
                  <th
                    key={header}
                    className="px-7 py-5 text-start text-[11px] font-semibold uppercase tracking-[0.16em] text-muted"
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {analysisRows.map((row) => (
                <tr
                  key={row.id}
                  className="border-b border-border-subtle transition-colors last:border-0 hover:bg-bg-light/35"
                >
                  <td className="px-7 py-6 text-[15px] font-semibold text-black-primary">
                    {row.category}
                  </td>
                  <td className="px-7 py-6 text-sm tabular-nums text-black-primary">
                    {formatAmount(row.amount)}
                  </td>
                  <td className="px-7 py-6 text-sm tabular-nums text-muted">
                    {row.percentage}
                  </td>
                  <td className="px-7 py-6">
                    <span className="rounded-full border border-border/70 bg-bg-light px-3 py-1 text-xs font-medium text-gray-medium">
                      {row.department}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-border/60 bg-surface">
        <div className="border-b border-border/60 px-7 py-5">
          <h3 className="text-base font-semibold text-black-primary">
            تفاصيل الهدر — الموردون
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse">
            <thead>
              <tr className="border-b border-border/70 bg-bg-light/50">
                {["المورد", "الفئة", "المبلغ (ر.س)", "الانحراف", "الحالة"].map(
                  (header) => (
                    <th
                      key={header}
                      className="px-7 py-5 text-start text-[11px] font-semibold uppercase tracking-[0.16em] text-muted"
                    >
                      {header}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {vendorRows.map((row) => (
                <tr
                  key={row.id}
                  className="border-b border-border-subtle transition-colors last:border-0 hover:bg-bg-light/35"
                >
                  <td className="px-7 py-6 text-[15px] font-semibold text-black-primary">
                    {row.vendor}
                  </td>
                  <td className="px-7 py-6">
                    <span className="rounded-full border border-border/70 bg-bg-light px-3 py-1 text-xs font-medium text-gray-medium">
                      {row.category}
                    </span>
                  </td>
                  <td className="px-7 py-6 text-sm tabular-nums text-black-primary">
                    {formatAmount(row.amount)}
                  </td>
                  <td className="px-7 py-6 text-sm font-medium text-warning">
                    {row.deviation}
                  </td>
                  <td className="px-7 py-6">
                    <Badge
                      variant={row.status === "حرج" ? "destructive" : "warning"}
                      className="px-3 py-1.5 text-xs font-semibold"
                    >
                      {row.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
