"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import type { RiskFindingView } from "@/lib/risk/view-types";
import { cn } from "@/lib/utils";

function priorityBadgeVariant(priority: string) {
  if (priority === "عالية") return "destructive" as const;
  if (priority === "متوسطة") return "warning" as const;
  return "secondary" as const;
}

export interface RiskFindingsTableProps {
  findings: RiskFindingView[];
  onReview: (findingId: string, action: string) => void;
  onPromote: (findingId: string) => void;
  busyFindingId?: string | null;
  className?: string;
}

export function RiskFindingsTable({
  findings,
  onReview,
  onPromote,
  busyFindingId,
  className,
}: RiskFindingsTableProps) {
  const columns: DataTableColumn<RiskFindingView>[] = [
    {
      key: "name",
      header: "النتيجة",
      className: "px-6 py-4 min-w-[180px]",
      cell: (row) => (
        <div className="space-y-1">
          <p className="text-[15px] font-semibold text-black-primary">{row.name}</p>
          <p className="text-xs text-muted">{row.category}</p>
        </div>
      ),
    },
    {
      key: "priority",
      header: "الأولوية",
      className: "px-6 py-4",
      cell: (row) => (
        <Badge variant={priorityBadgeVariant(row.priority)} className="text-xs">
          {row.priority}
        </Badge>
      ),
    },
    {
      key: "score",
      header: "الدرجة",
      className: "px-6 py-4 tabular-nums text-sm",
      cell: (row) => row.score,
    },
    {
      key: "status",
      header: "حالة المراجعة",
      className: "px-6 py-4",
      cell: (row) => (
        <Badge variant="outline" className="text-xs">
          {row.status}
        </Badge>
      ),
    },
    {
      key: "actions",
      header: "إجراءات",
      className: "px-6 py-4 min-w-[220px]",
      cell: (row) => {
        const busy = busyFindingId === row.id;
        const canPromote = row.statusCode === "reviewed" && !row.promotedRiskId;
        const canReview = !["promoted", "dismissed"].includes(row.statusCode);
        return (
          <div className="flex flex-wrap gap-2">
            {canReview ? (
              <>
                {row.statusCode === "detected" ? (
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={busy}
                    onClick={() => onReview(row.id, "request_review")}
                  >
                    مراجعة
                  </Button>
                ) : null}
                {["detected", "under_review"].includes(row.statusCode) ? (
                  <>
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={busy}
                      onClick={() => onReview(row.id, "approve")}
                    >
                      اعتماد
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      disabled={busy}
                      onClick={() => onReview(row.id, "reject")}
                    >
                      رفض
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      disabled={busy}
                      onClick={() => onReview(row.id, "dismiss")}
                    >
                      تجاهل
                    </Button>
                  </>
                ) : null}
              </>
            ) : null}
            {canPromote ? (
              <Button size="sm" disabled={busy} onClick={() => onPromote(row.id)}>
                إضافة إلى سجل المخاطر
              </Button>
            ) : null}
            {row.promotedRiskId ? (
              <Link
                href={`/risk-management/risks/${row.promotedRiskId}`}
                className="text-xs font-semibold text-gold-dark hover:underline"
              >
                عرض في السجل
              </Link>
            ) : null}
            {row.statusCode === "dismissed" ? (
              <Button
                size="sm"
                variant="ghost"
                disabled={busy}
                onClick={() => onReview(row.id, "reopen")}
              >
                إعادة فتح
              </Button>
            ) : null}
          </div>
        );
      },
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={findings}
      className={cn("rounded-2xl border-border/60 shadow-none", className)}
    />
  );
}
