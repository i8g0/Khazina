import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { RecentAnalysis } from "@/lib/placeholder-data";

function FileTypeBadge({ filename }: { filename: string }) {
  const extension = filename.split(".").pop()?.toUpperCase() ?? "FILE";

  return (
    <span className="inline-flex items-center gap-2.5">
      <span className="rounded-md border border-border/70 bg-bg-light px-2 py-1 text-[10px] font-bold tracking-wider text-gray-medium">
        {extension}
      </span>
      <span className="font-mono text-sm text-muted">{filename}</span>
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const isComplete = status === "مكتمل";

  return (
    <Badge
      variant={isComplete ? "success" : "warning"}
      className="px-3 py-1.5 text-xs font-semibold"
    >
      {status}
    </Badge>
  );
}

export interface DashboardAnalysesTableProps {
  data: RecentAnalysis[];
  className?: string;
}

export function DashboardAnalysesTable({
  data,
  className,
}: DashboardAnalysesTableProps) {
  return (
    <div
      className={cn(
        "overflow-hidden rounded-2xl border border-border/60 bg-surface",
        className,
      )}
    >
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] border-collapse">
          <thead>
            <tr className="border-b border-border/70 bg-bg-light/50">
              {[
                "العنوان",
                "النوع",
                "الملف",
                "التاريخ",
                "الحالة",
              ].map((header) => (
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
            {data.map((row) => (
              <tr
                key={row.id}
                className="border-b border-border-subtle transition-colors last:border-0 hover:bg-bg-light/35"
              >
                <td className="px-6 py-4 text-[15px] font-semibold text-black-primary">
                  {row.title}
                </td>
                <td className="px-6 py-4">
                  <span className="rounded-full border border-border/70 bg-bg-light px-3 py-1 text-xs font-medium text-gray-medium">
                    {row.type}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <FileTypeBadge filename={row.sourceFile} />
                </td>
                <td className="px-6 py-4 text-sm tabular-nums text-muted">
                  {row.date}
                </td>
                <td className="px-6 py-4">
                  <StatusBadge status={row.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
