"use client";

import { cn } from "@/lib/utils";
import { SidebarMobileTrigger } from "@/components/layout/sidebar-shell";

export interface HeaderShellProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  leading?: React.ReactNode;
  actions?: React.ReactNode;
  onMobileMenuClick?: () => void;
  variant?: "default" | "executive";
  className?: string;
}

export function HeaderShell({
  title,
  subtitle,
  leading,
  actions,
  onMobileMenuClick,
  variant = "default",
  className,
}: HeaderShellProps) {
  const isExecutive = variant === "executive";

  return (
    <header
      className={cn(
        "sticky top-0 z-30 flex items-center justify-between gap-4 border-b bg-surface/95 backdrop-blur",
        isExecutive ? "h-[76px] border-border/60 px-6 md:px-10" : "h-16 border-border px-4 md:px-6",
        className,
      )}
    >
      <div className="flex min-w-0 items-center gap-3">
        <SidebarMobileTrigger onClick={onMobileMenuClick} />
        {leading}
        <div className="min-w-0 space-y-0.5">
          {title ? (
            <h1
              className={cn(
                "truncate font-semibold text-black-primary",
                isExecutive ? "text-2xl md:text-[1.75rem]" : "text-lg",
              )}
            >
              {title}
            </h1>
          ) : null}
          {subtitle ? (
            <p
              className={cn(
                "truncate text-muted",
                isExecutive ? "text-sm" : "text-xs",
              )}
            >
              {subtitle}
            </p>
          ) : null}
        </div>
      </div>
      {actions ? (
        <div className="flex shrink-0 items-center gap-2">{actions}</div>
      ) : null}
    </header>
  );
}
