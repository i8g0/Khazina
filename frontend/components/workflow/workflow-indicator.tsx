"use client";

import * as React from "react";
import Link from "next/link";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { useDemoArtifacts } from "@/lib/demo/hooks";
import {
  PIPELINE_STAGES,
  resolvePipelineStatuses,
  type PipelineStageId,
} from "@/lib/workflow/pipeline";

export interface WorkflowIndicatorProps {
  activeStageId?: PipelineStageId;
  className?: string;
}

export function WorkflowIndicator({
  activeStageId,
  className,
}: WorkflowIndicatorProps) {
  const artifacts = useDemoArtifacts();
  const statuses = resolvePipelineStatuses(artifacts, activeStageId);

  return (
    <nav
      aria-label="مسار التحليل التنفيذي"
      className={cn(
        "rounded-2xl border border-border/60 bg-surface px-4 py-4 md:px-5 md:py-4",
        className,
      )}
    >
      <p className="mb-3 text-xs font-semibold uppercase tracking-[0.14em] text-muted">
        مسار التحليل التنفيذي
      </p>
      <ol className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:gap-1">
        {PIPELINE_STAGES.map((stage, index) => {
          const status = statuses[index];
          const isLast = index === PIPELINE_STAGES.length - 1;

          return (
            <li
              key={stage.id}
              className="flex min-w-0 flex-1 items-center gap-1 sm:min-w-[120px] sm:flex-none"
            >
              <Link
                href={stage.href}
                className={cn(
                  "flex min-w-0 flex-1 items-center gap-2 rounded-xl border px-3 py-2 text-start transition-colors",
                  status.current
                    ? "border-gold-primary bg-gold-primary/[0.08] text-black-primary"
                    : status.completed
                      ? "border-border/50 bg-bg-light/50 text-gray-medium hover:bg-bg-light"
                      : "border-border/40 bg-surface text-muted hover:bg-bg-light/60",
                )}
                aria-current={status.current ? "step" : undefined}
              >
                <span
                  className={cn(
                    "flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold",
                    status.completed
                      ? "bg-gold-primary text-white"
                      : status.current
                        ? "border border-gold-primary bg-white text-gold-dark"
                        : "border border-border/70 bg-white text-muted",
                  )}
                >
                  {status.completed ? (
                    <Check className="h-3.5 w-3.5" strokeWidth={2.5} />
                  ) : (
                    index + 1
                  )}
                </span>
                <span className="min-w-0">
                  <span className="block truncate text-xs font-semibold sm:text-[13px]">
                    <span className="sm:hidden">{stage.shortLabel}</span>
                    <span className="hidden sm:inline">{stage.label}</span>
                  </span>
                </span>
              </Link>
              {!isLast ? (
                <span
                  aria-hidden="true"
                  className="hidden h-px w-3 shrink-0 bg-border/70 sm:block"
                />
              ) : null}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
