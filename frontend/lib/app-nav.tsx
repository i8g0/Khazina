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

export function getAppNavItems() {
  return dashboardNavItems.map((item) => ({
    id: item.id,
    label: item.label,
    href: navRouteMap[item.id],
    icon: navIcons[item.id] ?? (
      <BarChart3 className="h-[18px] w-[18px]" strokeWidth={1.75} />
    ),
  }));
}

export const executivePageContainerClassName =
  "max-w-[1760px] px-4 py-7 md:px-6 md:py-8 lg:px-8";

/** Unified vertical rhythm for executive pages (matches Dashboard density reference) */
export const executivePageSpacingClassName = "space-y-[2.75rem] md:space-y-[3.25rem]";

/** Spacing within a page section (header + content) */
export const executiveSectionSpacingClassName = "space-y-4 md:space-y-5";
