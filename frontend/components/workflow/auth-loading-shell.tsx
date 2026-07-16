import Image from "next/image";
import { LoadingSpinner } from "@/components/ui/loading-spinner";

export function AuthLoadingShell() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-bg-light px-4">
      <div className="flex flex-col items-center gap-5 text-center">
        <span className="flex h-16 w-16 items-center justify-center rounded-2xl border border-border/60 bg-surface p-2 shadow-soft">
          <Image
            src="/khazina-logo.png?v=2"
            alt="شعار خزينة"
            width={48}
            height={48}
            className="h-full w-full object-contain"
          />
        </span>
        <div className="space-y-2">
          <LoadingSpinner size="md" label="جاري تحميل المنصة" />
          <p className="text-sm font-medium text-black-primary">
            جاري تحميل المنصة...
          </p>
          <p className="text-xs text-muted">يرجى الانتظار لحظات</p>
        </div>
      </div>
    </div>
  );
}
