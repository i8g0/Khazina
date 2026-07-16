"use client";

import { ShieldOff } from "lucide-react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHero } from "@/components/ui/page-hero";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  getAppNavGroups,
} from "@/lib/app-nav";
import { useRequireAuth } from "@/lib/auth/auth-context";
import { useOrganizationDisplay } from "@/lib/org-lookups";

export function RiskPage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="إدارة المخاطر"
      subtitle={org.reportingPeriod ?? undefined}
      activeItemId="risk"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="إدارة المخاطر"
            description="متابعة وتحليل المخاطر التشغيلية والمالية للمؤسسة."
            period={org.reportingPeriod}
          />

          <EmptyState
            title="محرك المخاطر غير مفعّل في هذا العرض"
            description="مسار العرض التنفيذي الحالي لا يتضمن محرك المخاطر. سيتم تفعيل هذه القدرة في مرحلة لاحقة من المنصة."
            icon={<ShieldOff className="h-6 w-6" />}
            className="min-h-[420px] rounded-2xl"
          />
        </div>
      </PageContainer>
    </AppLayout>
  );
}
