import {
  BarChart3,
  Database,
  FileBarChart,
  LayoutDashboard,
  LineChart,
  ScanSearch,
  ShieldAlert,
} from "lucide-react";
import { dashboardNavItems } from "@/lib/placeholder-data";

export const navRouteMap: Record<string, string> = {
  dashboard: "/",
  waste: "/financial-waste",
};

export const navIcons: Record<string, React.ReactNode> = {
  dashboard: <LayoutDashboard className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  waste: <ScanSearch className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  risk: <ShieldAlert className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  simulation: <LineChart className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  reports: <FileBarChart className="h-[18px] w-[18px]" strokeWidth={1.75} />,
  data: <Database className="h-[18px] w-[18px]" strokeWidth={1.75} />,
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
  "max-w-[1720px] px-5 py-12 md:px-8 md:py-14 lg:px-10";
