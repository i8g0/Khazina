import { cn } from "@/lib/utils";

export interface DashboardHeroProps {
  title: string;
  description?: string;
  period: string;
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
        "relative min-h-[220px] overflow-hidden rounded-2xl border border-border/60 bg-surface md:min-h-[260px]",
        className,
      )}
    >
      <span
        aria-hidden="true"
        className="absolute inset-y-0 start-0 w-1.5 bg-gold-primary"
      />
      <div className="flex min-h-[inherit] flex-col justify-center px-10 py-14 md:px-14 md:py-16 lg:px-16">
        <div className="flex flex-col gap-10 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-4xl space-y-5">
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-gold-dark">
              لوحة التحكم التنفيذية
            </p>
            <div className="space-y-4">
              <h1 className="text-[2.75rem] font-semibold leading-[1.02] tracking-tight text-black-primary md:text-[3.5rem] lg:text-[3.75rem]">
                {title}
              </h1>
              {description ? (
                <p className="max-w-3xl text-lg leading-relaxed text-gray-medium md:text-xl md:leading-8">
                  {description}
                </p>
              ) : null}
            </div>
          </div>
          <div className="shrink-0">
            <span className="inline-flex items-center rounded-full border border-gold-primary/30 bg-gold-primary/[0.07] px-5 py-2.5 text-base font-medium text-gold-dark">
              {period}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
