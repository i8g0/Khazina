import Image from "next/image";
import { cn } from "@/lib/utils";

export interface DashboardHeroProps {
  title: string;
  description?: string;
  period?: string | null;
  className?: string;
}

export function DashboardHero({
  title,
  description,
  period,
  className,
}: DashboardHeroProps) {
  return (
    <section
      className={cn(
        "relative min-h-[104px] overflow-hidden rounded-2xl border border-border/60 bg-surface md:min-h-[118px]",
        className,
      )}
    >
      <span
        aria-hidden="true"
        className="absolute inset-y-0 start-0 w-1.5 bg-gold-primary"
      />
      <div className="flex min-h-[inherit] flex-col justify-center px-6 py-4 md:px-8 md:py-4 lg:px-9">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-4xl space-y-1.5">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-gold-dark">
              لوحة التحكم التنفيذية
            </p>
            <div className="space-y-1.5">
              <h1 className="text-[1.75rem] font-semibold leading-[1.05] tracking-tight text-black-primary md:text-[2.15rem] lg:text-[2.35rem]">
                {title}
              </h1>
              {description ? (
                <p className="max-w-3xl text-[15px] leading-relaxed text-gray-medium md:text-base">
                  {description}
                </p>
              ) : null}
            </div>
          </div>
          <div className="flex shrink-0 flex-col items-center gap-2.5">
            <span className="flex h-14 w-14 items-center justify-center rounded-xl border border-border/50 bg-white p-1 shadow-soft md:h-16 md:w-16 md:p-1">
              <Image
                src="/khazina-logo.png?v=2"
                alt="شعار خزينة"
                width={56}
                height={56}
                className="h-full w-full object-contain"
              />
            </span>
            <span className="inline-flex items-center rounded-full border border-gold-primary/30 bg-gold-primary/[0.07] px-3.5 py-1.5 text-sm font-medium text-gold-dark">
              {period ?? "لم تُحدَّد فترة تقرير نشطة"}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
