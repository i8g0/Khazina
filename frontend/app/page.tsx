import { LayoutTemplate } from "lucide-react";
import { AppLayout, PageContainer } from "@/components/layout";
import { EmptyState, SectionHeader } from "@/components/ui";
import { SITE_DESCRIPTION, SITE_NAME } from "./site";

export default function Home() {
  return (
    <AppLayout
      brand={
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gold-primary text-sm font-bold text-white">
            خ
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-black-primary">
              {SITE_NAME}
            </p>
            <p className="truncate text-xs text-muted">منصة مؤسسية</p>
          </div>
        </div>
      }
      title="أساسيات نظام التصميم"
      subtitle="أساسيات نظام التصميم"
    >
      <PageContainer>
        <div className="space-y-8">
          <SectionHeader
            title="البنية التحتية للواجهة"
            description="مكونات قابلة لإعادة الاستخدام جاهزة لبناء منصة خزينة دون منطق أعمال."
          />

          <EmptyState
            title="نظام التصميم جاهز"
            description={SITE_DESCRIPTION}
            icon={<LayoutTemplate className="h-6 w-6" />}
          />
        </div>
      </PageContainer>
    </AppLayout>
  );
}
