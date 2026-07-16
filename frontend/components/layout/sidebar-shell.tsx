"use client";

import * as React from "react";
import Link from "next/link";
import { Menu, PanelRightClose, PanelRightOpen, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import type { AppNavGroup } from "@/lib/app-nav";
import { Button } from "@/components/ui/button";
import { slideInFromEnd } from "@/lib/motion";

export interface SidebarNavItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  href?: string;
}

export interface SidebarShellProps {
  brand: React.ReactNode;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  navItems?: SidebarNavItem[];
  navGroups?: AppNavGroup[];
  activeItemId?: string;
  onNavItemClick?: (item: SidebarNavItem) => void;
  collapsed?: boolean;
  onCollapsedChange?: (collapsed: boolean) => void;
  mobileOpen?: boolean;
  onMobileOpenChange?: (open: boolean) => void;
  variant?: "default" | "executive";
  className?: string;
}

function SidebarNavLink({
  item,
  isActive,
  collapsed,
  isExecutive,
  onNavItemClick,
}: {
  item: SidebarNavItem;
  isActive: boolean;
  collapsed?: boolean;
  isExecutive: boolean;
  onNavItemClick?: (item: SidebarNavItem) => void;
}) {
  const itemClassName = cn(
    "relative flex w-full items-center gap-3 rounded-xl font-medium transition-all",
    isExecutive
      ? cn(
          "px-4 py-3.5 text-[15px]",
          isActive
            ? "bg-gold-primary text-white shadow-none"
            : "text-gray-medium hover:bg-bg-light hover:text-black-primary",
        )
      : cn(
          "px-3.5 py-3 text-sm",
          isActive
            ? "bg-gold-primary/10 text-gold-dark"
            : "text-gray-medium hover:bg-bg-light hover:text-black-primary",
        ),
    collapsed && "justify-center px-2",
  );
  const itemContent = (
    <>
      {item.icon ? (
        <span className="shrink-0 text-current">{item.icon}</span>
      ) : null}
      {!collapsed ? <span className="truncate">{item.label}</span> : null}
    </>
  );

  if (item.href) {
    return (
      <Link
        href={item.href}
        className={itemClassName}
        onClick={() => onNavItemClick?.(item)}
      >
        {itemContent}
      </Link>
    );
  }

  return (
    <button
      type="button"
      onClick={() => onNavItemClick?.(item)}
      className={itemClassName}
    >
      {itemContent}
    </button>
  );
}

function SidebarPanel({
  brand,
  children,
  footer,
  navItems,
  navGroups,
  activeItemId,
  onNavItemClick,
  collapsed,
  onCollapsedChange,
  onClose,
  showCollapseToggle,
  showCloseButton,
  variant = "default",
  className,
}: {
  brand: React.ReactNode;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  navItems: SidebarNavItem[];
  navGroups?: AppNavGroup[];
  activeItemId?: string;
  onNavItemClick?: (item: SidebarNavItem) => void;
  collapsed?: boolean;
  onCollapsedChange?: (collapsed: boolean) => void;
  onClose?: () => void;
  showCollapseToggle?: boolean;
  showCloseButton?: boolean;
  variant?: "default" | "executive";
  className?: string;
}) {
  const isExecutive = variant === "executive";
  const renderedBrand =
    React.isValidElement(brand) && collapsed !== undefined
      ? React.cloneElement(brand as React.ReactElement<{ collapsed?: boolean }>, {
          collapsed,
        })
      : brand;

  return (
    <aside
      className={cn(
        "flex h-full flex-col border-e",
        isExecutive
          ? "border-border/70 bg-surface shadow-none"
          : "border-border bg-surface shadow-soft",
        collapsed ? "w-[88px]" : isExecutive ? "w-[272px]" : "w-[280px]",
        className,
      )}
    >
      <div
        className={cn(
          "flex items-center justify-between gap-2 border-b px-5",
          isExecutive
            ? "min-h-[104px] border-border/70 py-6"
            : "h-16 border-border px-4",
        )}
      >
        <div className={cn("min-w-0 flex-1", collapsed && "flex justify-center")}>
          {renderedBrand}
        </div>
        {showCollapseToggle ? (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onCollapsedChange?.(!collapsed)}
            aria-label={collapsed ? "توسيع القائمة الجانبية" : "طي القائمة الجانبية"}
            className={cn(isExecutive && "text-muted hover:bg-bg-light hover:text-black-primary")}
          >
            {collapsed ? (
              <PanelRightOpen className="h-4 w-4" />
            ) : (
              <PanelRightClose className="h-4 w-4" />
            )}
          </Button>
        ) : null}
        {showCloseButton ? (
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            aria-label="إغلاق القائمة"
            className={cn(isExecutive && "text-muted hover:bg-bg-light hover:text-black-primary")}
          >
            <X className="h-4 w-4" />
          </Button>
        ) : null}
      </div>

      <nav className={cn("flex-1 overflow-y-auto", isExecutive ? "space-y-4 px-4 py-5" : "space-y-1 p-3")}>
        {navGroups && navGroups.length > 0 ? (
          navGroups.map((group) => (
            <div key={group.id} className="space-y-1.5">
              {!collapsed ? (
                <p
                  className={cn(
                    "px-2 pb-1 text-[11px] font-semibold uppercase tracking-[0.12em]",
                    group.variant === "deferred"
                      ? "text-muted/80"
                      : "text-muted",
                  )}
                >
                  {group.label}
                </p>
              ) : null}
              <div className="space-y-1.5">
                {group.items.map((item) => (
                  <SidebarNavLink
                    key={item.id}
                    item={item}
                    isActive={item.id === activeItemId}
                    collapsed={collapsed}
                    isExecutive={isExecutive}
                    onNavItemClick={onNavItemClick}
                  />
                ))}
              </div>
            </div>
          ))
        ) : (
          navItems.map((item) => (
            <SidebarNavLink
              key={item.id}
              item={item}
              isActive={item.id === activeItemId}
              collapsed={collapsed}
              isExecutive={isExecutive}
              onNavItemClick={onNavItemClick}
            />
          ))
        )}
        {children}
      </nav>

      {footer ? (
        <div
          className={cn(
            "border-t p-4",
            isExecutive ? "border-border/70" : "border-border",
          )}
        >
          {footer}
        </div>
      ) : null}
    </aside>
  );
}

export function SidebarShell({
  brand,
  children,
  footer,
  navItems = [],
  navGroups,
  activeItemId,
  onNavItemClick,
  collapsed = false,
  onCollapsedChange,
  mobileOpen = false,
  onMobileOpenChange,
  variant = "default",
  className,
}: SidebarShellProps) {
  const panelProps = {
    brand,
    children,
    footer,
    navItems,
    navGroups,
    activeItemId,
    onNavItemClick,
    collapsed,
    onCollapsedChange,
    variant,
    className,
  };

  return (
    <>
      <div className="hidden shrink-0 self-start md:sticky md:top-0 md:z-30 md:block md:h-screen lg:sticky lg:top-0 lg:z-30 lg:h-screen">
        <SidebarPanel {...panelProps} showCollapseToggle />
      </div>

      <AnimatePresence>
        {mobileOpen ? (
          <>
            <motion.button
              type="button"
              aria-label="إغلاق الخلفية"
              className="fixed inset-0 z-40 bg-black-primary/40 md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => onMobileOpenChange?.(false)}
            />
            <motion.div
              className="fixed inset-y-0 start-0 z-50 md:hidden"
              variants={slideInFromEnd}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <SidebarPanel
                {...panelProps}
                collapsed={false}
                showCloseButton
                onClose={() => onMobileOpenChange?.(false)}
              />
            </motion.div>
          </>
        ) : null}
      </AnimatePresence>
    </>
  );
}

export function SidebarMobileTrigger({
  onClick,
  className,
}: {
  onClick?: () => void;
  className?: string;
}) {
  return (
    <Button
      variant="ghost"
      size="icon"
      className={cn("md:hidden", className)}
      onClick={onClick}
      aria-label="فتح القائمة"
    >
      <Menu className="h-5 w-5" />
    </Button>
  );
}
