"use client";

import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
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
        <div className="border-b border-border/60 px-6 py-3.5">
          <h3 className="text-base font-semibold text-black-primary">
            تفصيل الهدر — الفئات
          </h3>
        </div>
        {analysisRows.length === 0 ? (
          <EmptyState
            title="لا توجد فئات هدر"
            description="لم يُرجع التحليل أي تفصيل فئات لهذا التشغيل."
            className="border-none bg-transparent py-10 shadow-none"
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse">
              <thead>
                <tr className="border-b border-border/70 bg-bg-light/50">
                  {["الفئة", "المبلغ (ر.س)", "النسبة", "الإدارة"].map((header) => (
                    <th
                      key={header}
                      className="px-6 py-3.5 text-start text-[11px] font-semibold uppercase tracking-[0.16em] text-muted"
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
                    <td className="px-6 py-4 text-[15px] font-semibold text-black-primary">
                      {row.category}
                    </td>
                    <td className="px-6 py-4 text-sm tabular-nums text-black-primary">
                      {formatAmount(row.amount)}
                    </td>
                    <td className="px-6 py-4 text-sm tabular-nums text-muted">
                      {row.percentage}
                    </td>
                    <td className="px-6 py-4">
                      {row.department ? (
                        <span className="rounded-full border border-border/70 bg-bg-light px-3 py-1 text-xs font-medium text-gray-medium">
                          {row.department}
                        </span>
                      ) : (
                        <span className="text-xs text-muted">لم يُربط بقسم</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {vendorRows.length > 0 ? (
        <div className="overflow-hidden rounded-2xl border border-border/60 bg-surface">
          <div className="border-b border-border/60 px-6 py-3.5">
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
                        className="px-6 py-3.5 text-start text-[11px] font-semibold uppercase tracking-[0.16em] text-muted"
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
                    <td className="px-6 py-4 text-[15px] font-semibold text-black-primary">
                      {row.vendor}
                    </td>
                    <td className="px-6 py-4">
                      <span className="rounded-full border border-border/70 bg-bg-light px-3 py-1 text-xs font-medium text-gray-medium">
                        {row.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm tabular-nums text-black-primary">
                      {formatAmount(row.amount)}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-warning">
                      {row.deviation}
                    </td>
                    <td className="px-6 py-4">
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
      ) : (
        <EmptyState
          title="لا تتوفر نتائج على مستوى المورد"
          description="لا تتوفر حالياً نتائج تفصيلية على مستوى الموردين لهذا الملف. ستظهر هنا عند توفرها من التحليل."
          className="rounded-2xl"
        />
      )}
    </div>
  );
}
