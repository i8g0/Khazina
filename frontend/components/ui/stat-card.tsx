import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";

export interface StatCardProps {
  label: string;
  value: React.ReactNode;
  hint?: string;
  departmentBadge?: string;
  icon?: React.ReactNode;
  trend?: React.ReactNode;
  className?: string;
}

export function StatCard({
  label,
  value,
  hint,
  departmentBadge,
  icon,
  trend,
  className,
}: StatCardProps) {
  return (
    <Card className={cn("hover:shadow-card", className)}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              {departmentBadge ? (
                <span className="rounded-full bg-gold-primary/10 px-2 py-0.5 text-xs font-medium text-gold-dark">
                  {departmentBadge}
                </span>
              ) : null}
            </div>
            <p className="text-sm font-medium text-muted">{label}</p>
            <p className="text-3xl font-semibold tracking-tight text-black-primary">
              {value}
            </p>
            {hint ? <p className="text-xs text-muted">{hint}</p> : null}
          </div>
          {icon ? (
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gold-primary/10 text-gold-primary">
              {icon}
            </div>
          ) : null}
        </div>
        {trend ? <div className="mt-4">{trend}</div> : null}
      </CardContent>
    </Card>
  );
}
