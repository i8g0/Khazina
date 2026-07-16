"use client";

import Link from "next/link";
import { ArrowLeft, PlayCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useDemoArtifacts } from "@/lib/demo/hooks";
import {
  getContinueTarget,
  hasActiveAnalysis,
  isAnalysisComplete,
} from "@/lib/workflow/pipeline";
import { navRouteMap } from "@/lib/app-nav";

export interface DashboardGuidanceHeroProps {
  orgName: string;
  executiveTitle: string;
  period?: string | null;
  className?: string;
}

export function DashboardGuidanceHero({
  orgName,
  executiveTitle,
  period,
  className,
}: DashboardGuidanceHeroProps) {
  const artifacts = useDemoArtifacts();
  const continueTarget = getContinueTarget(artifacts);
  const active = hasActiveAnalysis(artifacts);
  const complete = isAnalysisComplete(artifacts);

  const headline = complete
    ? "اكتمل التحليل التنفيذي"
    : active
      ? "تابع مسار التحليل المالي"
      : "ابدأ التحليل المالي";

  const description = complete
    ? "خزينة حلّلت بياناتك المالية وولّدت توصيات وتقريراً تنفيذياً. يمكنك مراجعة النتائج أو بدء تحليل جديد."
    : active
      ? "لديك تحليل قيد التقدم. تابع من حيث توقفت لإكمال التوصيات والمحاكاة والتقرير."
      : "خزينة منصة تنفيذية لاكتشاف الهدر المالي، توليد التوصيات، ومحاكاة السيناريوهات — ابدأ برفع ملفك المالي.";

  return (
    <section
      className={cn(
        "relative overflow-hidden rounded-2xl border border-border/60 bg-surface",
        className,
      )}
    >
      <span
        aria-hidden="true"
        className="absolute inset-y-0 start-0 w-1.5 bg-gold-primary"
      />
      <div className="flex flex-col gap-5 px-6 py-5 md:px-8 md:py-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-2xl space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-dark">
            {executiveTitle} — {orgName}
          </p>
          <h1 className="text-[1.65rem] font-semibold leading-tight tracking-tight text-black-primary md:text-[2rem]">
            {headline}
          </h1>
          <p className="text-[15px] leading-relaxed text-gray-medium md:text-base">
            {description}
          </p>
          {period ? (
            <p className="text-sm text-muted">فترة التقرير: {period}</p>
          ) : null}
        </div>

        <div className="flex shrink-0 flex-col gap-3 sm:flex-row lg:flex-col xl:flex-row">
          <Button asChild size="lg" className="min-w-[200px]">
            <Link href={navRouteMap.data}>
              <PlayCircle className="h-4 w-4" />
              {complete ? "تحليل مجموعة جديدة" : "بدء التحليل المالي"}
            </Link>
          </Button>
          {continueTarget && !complete ? (
            <Button asChild variant="secondary" size="lg" className="min-w-[200px]">
              <Link href={continueTarget.href}>
                <ArrowLeft className="h-4 w-4" />
                {continueTarget.label}
              </Link>
            </Button>
          ) : null}
          {complete && continueTarget ? (
            <Button asChild variant="secondary" size="lg" className="min-w-[200px]">
              <Link href={continueTarget.href}>
                <ArrowLeft className="h-4 w-4" />
                {continueTarget.label}
              </Link>
            </Button>
          ) : null}
        </div>
      </div>
    </section>
  );
}
