"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { HeaderShell } from "@/components/layout/header-shell";
import {
  SidebarShell,
  type SidebarNavItem,
} from "@/components/layout/sidebar-shell";
import type { AppNavGroup } from "@/lib/app-nav";

export interface AppLayoutProps {
  children: React.ReactNode;
  brand: React.ReactNode;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  headerActions?: React.ReactNode;
  sidebarFooter?: React.ReactNode;
  sidebarContent?: React.ReactNode;
  navItems?: SidebarNavItem[];
  navGroups?: AppNavGroup[];
  activeItemId?: string;
  onNavItemClick?: (item: SidebarNavItem) => void;
  sidebarVariant?: "default" | "executive";
  className?: string;
  contentClassName?: string;
}

export function AppLayout({
  children,
  brand,
  title,
  subtitle,
  headerActions,
  sidebarFooter,
  sidebarContent,
  navItems = [],
  navGroups,
  activeItemId,
  onNavItemClick,
  sidebarVariant = "default",
  className,
  contentClassName,
}: AppLayoutProps) {
  const [collapsed, setCollapsed] = React.useState(false);
  const [mobileOpen, setMobileOpen] = React.useState(false);

  return (
    <div className={cn("flex min-h-screen bg-bg-light", className)}>
      <SidebarShell
        brand={brand}
        footer={sidebarFooter}
        navItems={navItems}
        navGroups={navGroups}
        activeItemId={activeItemId}
        onNavItemClick={onNavItemClick}
        collapsed={collapsed}
        onCollapsedChange={setCollapsed}
        mobileOpen={mobileOpen}
        onMobileOpenChange={setMobileOpen}
        variant={sidebarVariant}
      >
        {sidebarContent}
      </SidebarShell>

      <div className="flex min-w-0 flex-1 flex-col">
        <HeaderShell
          title={title}
          subtitle={subtitle}
          actions={headerActions}
          onMobileMenuClick={() => setMobileOpen(true)}
          variant={sidebarVariant}
        />
        <main className={cn("flex-1 overflow-auto", contentClassName)}>
          {children}
        </main>
      </div>
    </div>
  );
}
