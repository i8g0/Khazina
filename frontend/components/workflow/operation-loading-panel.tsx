import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { cn } from "@/lib/utils";

export interface OperationLoadingPanelProps {
  title: string;
  description?: string;
  className?: string;
}

export function OperationLoadingPanel({
  title,
  description,
  className,
}: OperationLoadingPanelProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        "flex min-h-[200px] flex-col items-center justify-center gap-4 rounded-2xl border border-border/60 bg-surface px-6 py-10 text-center",
        className,
      )}
    >
      <LoadingSpinner size="lg" label={title} />
      <div className="max-w-md space-y-1">
        <p className="text-base font-semibold text-black-primary">{title}</p>
        {description ? (
          <p className="text-sm leading-relaxed text-muted">{description}</p>
        ) : null}
      </div>
    </div>
  );
}
