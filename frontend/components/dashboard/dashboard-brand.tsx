import Image from "next/image";
import { cn } from "@/lib/utils";
import { SITE_NAME } from "@/app/site";

export function DashboardBrand({
  collapsed = false,
}: {
  collapsed?: boolean;
}) {
  if (collapsed) {
    return (
      <div className="flex justify-center py-1">
        <Image
          src="/brand/khazina-logo-white.png?v=2"
          alt={SITE_NAME}
          width={48}
          height={48}
          className="h-12 w-12 object-contain"
          priority
        />
      </div>
    );
  }

  return (
    <div className={cn("flex items-center gap-4 py-1")}>
      <Image
        src="/brand/khazina-logo-white.png?v=2"
        alt={SITE_NAME}
        width={60}
        height={60}
        className="h-[60px] w-[60px] shrink-0 object-contain"
        priority
      />
      <div className="min-w-0 space-y-1">
        <p className="truncate text-base font-semibold tracking-tight text-black-primary">
          Khazina
        </p>
        <p className="truncate text-xs font-medium tracking-wide text-muted">
          Executive Intelligence
        </p>
      </div>
    </div>
  );
}
