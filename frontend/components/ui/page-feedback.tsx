import { Alert } from "@/components/ui/alert";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";

/** Shared page feedback block — use one pattern across executive pages. */
export function PageFeedback({
  loading,
  error,
  message,
  empty,
  onRetry,
  skeletonClassName = "min-h-[280px] rounded-2xl",
  children,
}: {
  loading?: boolean;
  error?: string | null;
  message?: string | null;
  empty?: { title: string; description?: string } | null;
  onRetry?: () => void;
  skeletonClassName?: string;
  children?: React.ReactNode;
}) {
  const showEmpty = Boolean(!loading && !error && empty);
  const showChildren = Boolean(!loading && !showEmpty && children);

  return (
    <>
      {message ? (
        <Alert variant="success" title="تم">
          {message}
        </Alert>
      ) : null}
      {error ? (
        <ErrorState title="خطأ" description={error} onRetry={onRetry} />
      ) : null}
      {loading ? (
        <div role="status" aria-live="polite" aria-label="جاري التحميل">
          <LoadingSkeleton className={skeletonClassName} />
        </div>
      ) : null}
      {showEmpty && empty ? (
        <EmptyState title={empty.title} description={empty.description} />
      ) : null}
      {showChildren ? children : null}
    </>
  );
}
