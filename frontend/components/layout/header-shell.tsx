"use client";

import { cn } from "@/lib/utils";
import { SidebarMobileTrigger } from "@/components/layout/sidebar-shell";

export interface HeaderShellProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  leading?: React.ReactNode;
  actions?: React.ReactNode;
  onMobileMenuClick?: () => void;
  className?: string;
}

export function HeaderShell({
  title,
  subtitle,
  leading,
  actions,
  onMobileMenuClick,
  className,
}: HeaderShellProps) {
  return (
    <header
      className={cn(
        "sticky top-0 z-30 flex h-16 items-center justify-between gap-4 border-b border-border bg-surface/95 px-4 backdrop-blur md:px-6",
        className,
      )}
    >
      <div className="flex min-w-0 items-center gap-3">
        <SidebarMobileTrigger onClick={onMobileMenuClick} />
        {leading}
        <div className="min-w-0">
          {title ? (
            <h1 className="truncate text-lg font-semibold text-black-primary">
              {title}
            </h1>
          ) : null}
          {subtitle ? (
            <p className="truncate text-xs text-muted">{subtitle}</p>
          ) : null}
        </div>
      </div>
      {actions ? (
        <div className="flex shrink-0 items-center gap-2">{actions}</div>
      ) : null}
    </header>
  );
}
