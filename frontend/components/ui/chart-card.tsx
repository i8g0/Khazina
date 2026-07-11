"use client";

import { cn } from "@/lib/utils";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";

export interface ChartCardProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  children?: React.ReactNode;
  emptyTitle?: string;
  emptyDescription?: string;
  className?: string;
  height?: number;
}

export function ChartCard({
  title,
  description,
  action,
  children,
  emptyTitle = "لا توجد بيانات للعرض",
  emptyDescription = "سيظهر الرسم البياني هنا عند توفر البيانات.",
  className,
  height = 320,
}: ChartCardProps) {
  return (
    <Card className={className}>
      <CardHeader className="flex-row items-start justify-between space-y-0">
        <div className="space-y-1">
          <CardTitle>{title}</CardTitle>
          {description ? <CardDescription>{description}</CardDescription> : null}
        </div>
        {action ? <div className="shrink-0">{action}</div> : null}
      </CardHeader>
      <CardContent>
        <div
          className={cn("w-full overflow-hidden rounded-lg border border-border-subtle bg-bg-light/50")}
          style={{ minHeight: height }}
        >
          {children ?? (
            <EmptyState
              className="h-full min-h-[inherit] border-0 bg-transparent shadow-none"
              title={emptyTitle}
              description={emptyDescription}
            />
          )}
        </div>
      </CardContent>
    </Card>
  );
}
