import {
  BarChart3,
  Bell,
  Building2,
  Database,
  FileBarChart,
  LayoutDashboard,
  LineChart,
  ScanSearch,
  Settings,
  ShieldAlert,
  Users,
} from "lucide-react";
import { dashboardNavItems } from "@/lib/placeholder-data";

export const navRouteMap: Record<string, string> = {
  dashboard: "/",
  waste: "/financial-waste",
  risk: "/risk-management",
  simulation: "/business-simulation",
  reports: "/reports",
  data: "/data-management",
  notifications: "/notifications",
  organization: "/organization",
  users: "/users",
  settings: "/settings",
};

export const navIcons: Record<string, React.ReactNode> = {
  dashboard: <LayoutDashboard className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  waste: <ScanSearch className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  risk: <ShieldAlert className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  simulation: <LineChart className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  reports: <FileBarChart className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  data: <Database className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  notifications: <Bell className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  organization: <Building2 className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  users: <Users className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  settings: <Settings className="h-[18px] w-[18px]" strokeWidth={1.75} />,
};

export interface AppNavItem {
  id: string;
  label: string;
  href: string;
  icon: React.ReactNode;
}

export interface AppNavGroup {
  id: string;
  label: string;
  items: AppNavItem[];
  variant?: "primary" | "secondary" | "deferred";
}

function buildNavItem(id: string, label: string): AppNavItem {
  return {
    id,
    label,
    href: navRouteMap[id],
    icon: navIcons[id] ?? (
      <BarChart3 className="h-[18px] w-[18px]" strokeWidth={1.75} />
    ),
  };
}

export function getAppNavItems(): AppNavItem[] {
  return dashboardNavItems.map((item) =>
    buildNavItem(item.id, item.label),
  );
}

export function getAppNavGroups(): AppNavGroup[] {
  const byId = Object.fromEntries(
    dashboardNavItems.map((item) => [item.id, item.label]),
  ) as Record<string, string>;

  return [
    {
      id: "analysis",
      label: "مسار التحليل التنفيذي",
      variant: "primary",
      items: ["data", "waste", "risk", "simulation", "reports"].map((id) =>
        buildNavItem(id, byId[id]),
      ),
    },
    {
      id: "overview",
      label: "نظرة عامة",
      variant: "secondary",
      items: ["dashboard", "notifications"].map((id) =>
        buildNavItem(id, byId[id]),
      ),
    },
    {
      id: "admin",
      label: "إدارة المنصة",
      variant: "secondary",
      items: ["organization", "users", "settings"].map((id) =>
        buildNavItem(id, byId[id]),
      ),
    },
  ];
}

export const executivePageContainerClassName =
  "max-w-[1760px] px-4 py-7 md:px-6 md:py-8 lg:px-8";

/** Unified vertical rhythm for executive pages (matches Dashboard density reference) */
export const executivePageSpacingClassName = "space-y-[2.75rem] md:space-y-[3.25rem]";

/** Spacing within a page section (header + content) */
export const executiveSectionSpacingClassName = "space-y-4 md:space-y-5";
