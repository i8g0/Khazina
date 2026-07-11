"use client";

import * as React from "react";
import { Menu, PanelRightClose, PanelRightOpen, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
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
  activeItemId?: string;
  onNavItemClick?: (item: SidebarNavItem) => void;
  collapsed?: boolean;
  onCollapsedChange?: (collapsed: boolean) => void;
  mobileOpen?: boolean;
  onMobileOpenChange?: (open: boolean) => void;
  className?: string;
}

function SidebarPanel({
  brand,
  children,
  footer,
  navItems,
  activeItemId,
  onNavItemClick,
  collapsed,
  onCollapsedChange,
  onClose,
  showCollapseToggle,
  showCloseButton,
  className,
}: {
  brand: React.ReactNode;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  navItems: SidebarNavItem[];
  activeItemId?: string;
  onNavItemClick?: (item: SidebarNavItem) => void;
  collapsed?: boolean;
  onCollapsedChange?: (collapsed: boolean) => void;
  onClose?: () => void;
  showCollapseToggle?: boolean;
  showCloseButton?: boolean;
  className?: string;
}) {
  return (
    <aside
      className={cn(
        "flex h-full flex-col border-e border-border bg-surface shadow-soft",
        collapsed ? "w-[88px]" : "w-[280px]",
        className,
      )}
    >
      <div className="flex h-16 items-center justify-between gap-2 border-b border-border px-4">
        {!collapsed ? <div className="min-w-0 flex-1">{brand}</div> : null}
        {showCollapseToggle ? (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onCollapsedChange?.(!collapsed)}
            aria-label={collapsed ? "توسيع القائمة الجانبية" : "طي القائمة الجانبية"}
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
          >
            <X className="h-4 w-4" />
          </Button>
        ) : null}
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {navItems.map((item) => {
          const isActive = item.id === activeItemId;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onNavItemClick?.(item)}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
                isActive
                  ? "bg-gold-primary/10 text-gold-dark"
                  : "text-gray-medium hover:bg-bg-light hover:text-black-primary",
                collapsed && "justify-center px-2",
              )}
            >
              {item.icon ? (
                <span className="shrink-0 text-current">{item.icon}</span>
              ) : null}
              {!collapsed ? <span className="truncate">{item.label}</span> : null}
            </button>
          );
        })}
        {children}
      </nav>

      {footer ? (
        <div className="border-t border-border p-4">{footer}</div>
      ) : null}
    </aside>
  );
}

export function SidebarShell({
  brand,
  children,
  footer,
  navItems = [],
  activeItemId,
  onNavItemClick,
  collapsed = false,
  onCollapsedChange,
  mobileOpen = false,
  onMobileOpenChange,
  className,
}: SidebarShellProps) {
  const panelProps = {
    brand,
    children,
    footer,
    navItems,
    activeItemId,
    onNavItemClick,
    collapsed,
    onCollapsedChange,
    className,
  };

  return (
    <>
      <div className="hidden shrink-0 lg:block">
        <SidebarPanel {...panelProps} showCollapseToggle />
      </div>

      <div className="hidden shrink-0 md:block lg:hidden">
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
