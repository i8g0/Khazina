"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowRight, Link2 } from "lucide-react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { RiskAiSummary } from "@/components/risk/risk-ai-summary";
import { RiskMitigationPlans } from "@/components/risk/risk-mitigation-plans";
import { RiskRecommendationCard } from "@/components/risk/risk-recommendation-card";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { AuthLoadingShell } from "@/components/workflow/auth-loading-shell";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavGroups,
  navRouteMap,
} from "@/lib/app-nav";
import {
  getRisk,
  getRiskAnalysis,
  getRiskHistory,
  getRiskProvenance,
  listRecommendations,
  listRiskMitigationPlans,
} from "@/lib/api/khazina-api";
import type { RiskEventResponse, RiskResponse } from "@/lib/api/types";
import { useRequireAuth, formatApiError } from "@/lib/auth/auth-context";
import {
  formatDate,
  formatRecommendationDisplay,
  mapLegacyRiskStatus,
  mapLifecycleStatus,
  mapRiskCategoryCode,
  mapRiskLevel,
  mapRiskPriority,
  mapRiskSourceType,
} from "@/lib/format";
import { mapMitigationPlan, mapRecommendation } from "@/lib/risk/mappers";
import { useOrganizationDisplay, useOrgLookups } from "@/lib/org-lookups";

export interface RiskDetailPageProps {
  riskId: string;
}

export function RiskDetailPage({ riskId }: RiskDetailPageProps) {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const { fileName } = useOrgLookups();

  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [risk, setRisk] = React.useState<RiskResponse | null>(null);
  const [history, setHistory] = React.useState<RiskEventResponse[]>([]);
  const [aiInsights, setAiInsights] = React.useState<Record<string, unknown> | null>(null);
  const [provenance, setProvenance] = React.useState<{
    runTitle?: string;
    runId?: string;
    snapshotLabel?: string;
  }>({});

  const load = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    try {
      const [riskData, events, prov] = await Promise.all([
        getRisk(auth.session.organizationId, auth.session.token, riskId),
        getRiskHistory(auth.session.organizationId, auth.session.token, riskId, {
          limit: 50,
        }),
        getRiskProvenance(auth.session.organizationId, auth.session.token, riskId),
      ]);
      setRisk(riskData);
      setHistory(events);

      let insights: Record<string, unknown> | null = null;
      let runTitle: string | undefined;
      if (prov.source_analysis_run_id) {
        const runDetail = await getRiskAnalysis(
          auth.session.organizationId,
          auth.session.token,
          prov.source_analysis_run_id,
        );
        runTitle = runDetail.analysis_run.title;
        const meta = runDetail.analysis_run.runtime_metadata?.ai_insights;
        if (meta && typeof meta === "object") {
          insights = meta as Record<string, unknown>;
        }
      }
      setAiInsights(insights);
      setProvenance({
        runTitle,
        runId: prov.source_analysis_run_id ?? undefined,
        snapshotLabel: prov.source_snapshot_id
          ? fileName(prov.source_snapshot_id) ?? prov.source_snapshot_id
          : undefined,
      });
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session, fileName, riskId]);

  React.useEffect(() => {
    void load();
  }, [load]);

  if (auth.isLoading) return <AuthLoadingShell />;
  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="تفاصيل الخطر"
      subtitle={org.reportingPeriod ?? undefined}
      activeItemId="risk"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="ghost" size="sm" asChild>
              <Link href={navRouteMap.risk}>
                <ArrowRight className="ms-2 h-4 w-4" />
                العودة إلى إدارة المخاطر
              </Link>
            </Button>
          </div>

          {loading ? (
            <LoadingSkeleton className="min-h-[320px] rounded-2xl" />
          ) : error ? (
            <ErrorState
              title="تعذّر تحميل تفاصيل الخطر"
              description={error}
              onRetry={() => void load()}
            />
          ) : risk ? (
            <>
              <header className="rounded-2xl border border-border/60 bg-surface px-5 py-5 md:px-6 md:py-6">
                <div className="mb-3 flex flex-wrap gap-2">
                  <Badge variant="destructive">{mapRiskPriority(risk.priority)}</Badge>
                  <Badge variant="outline">{mapLifecycleStatus(risk.lifecycle_status)}</Badge>
                  <Badge variant="secondary">{mapLegacyRiskStatus(risk.status)}</Badge>
                </div>
                <h1 className="mb-2 text-2xl font-semibold text-black-primary">{risk.name}</h1>
                <p className="text-sm leading-7 text-muted md:text-[15px]">{risk.description}</p>
                <dl className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <DetailItem label="الفئة" value={risk.category_label ?? mapRiskCategoryCode(risk.category_code)} />
                  <DetailItem label="المسؤول" value={risk.owner_label ?? "—"} />
                  <DetailItem label="الاحتمال" value={risk.likelihood ? mapRiskLevel(risk.likelihood) : "—"} />
                  <DetailItem label="الأثر" value={risk.impact ? mapRiskLevel(risk.impact) : "—"} />
                  <DetailItem label="الدرجة" value={String(risk.score)} />
                  <DetailItem label="المصدر" value={mapRiskSourceType(risk.source_type)} />
                  <DetailItem label="آخر تحديث" value={formatDate(risk.last_updated_at)} />
                  {risk.detected_at ? (
                    <DetailItem label="تاريخ الاكتشاف" value={formatDate(risk.detected_at)} />
                  ) : null}
                </dl>
              </header>

              {aiInsights ? (
                <RiskAiSummary
                  executiveSummary={
                    typeof aiInsights.risk_executive_summary === "string"
                      ? aiInsights.risk_executive_summary
                      : null
                  }
                  explanation={
                    typeof aiInsights.risk_explanation === "string"
                      ? aiInsights.risk_explanation
                      : null
                  }
                />
              ) : (
                <EmptyState
                  title="لا يوجد ملخص ذكاء اصطناعي"
                  description="ولّد ملخص المخاطر من صفحة إدارة المخاطر بعد التحليل"
                />
              )}

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader dense title="الارتباطات" />
                <div className="rounded-2xl border border-border/60 bg-surface px-5 py-4 text-sm text-muted">
                  <p className="inline-flex items-center gap-2">
                    <Link2 className="h-4 w-4" />
                    {provenance.runTitle
                      ? `تحليل مرتبط: ${provenance.runTitle}`
                      : "لا يوجد تحليل مرتبط"}
                  </p>
                  {provenance.snapshotLabel ? (
                    <p className="mt-2">لقطة مالية: {provenance.snapshotLabel}</p>
                  ) : null}
                </div>
              </section>

              <RiskDetailMitigation
                orgId={auth.session.organizationId}
                token={auth.session.token}
                riskId={riskId}
                riskName={risk.name}
                analysisRunId={provenance.runId}
              />

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader dense title="سجل التدقيق" />
                {history.length === 0 ? (
                  <EmptyState title="لا أحداث" description="لا يوجد سجل تدقيق لهذا الخطر" />
                ) : (
                  <ol className="space-y-3">
                    {history.map((event) => (
                      <li
                        key={event.id}
                        className="rounded-xl border border-border/60 bg-surface px-4 py-3 text-sm"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <span className="font-semibold text-black-primary">
                            {event.event_type}
                          </span>
                          <span className="text-xs text-muted">
                            {formatDate(event.created_at)}
                          </span>
                        </div>
                        {event.from_status || event.to_status ? (
                          <p className="mt-1 text-muted">
                            {event.from_status ?? "—"} ← {event.to_status ?? "—"}
                          </p>
                        ) : null}
                        {event.reason ? (
                          <p className="mt-1 text-muted">{event.reason}</p>
                        ) : null}
                      </li>
                    ))}
                  </ol>
                )}
              </section>
            </>
          ) : null}
        </div>
      </PageContainer>
    </AppLayout>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">
        {label}
      </dt>
      <dd className="mt-1 text-sm font-medium text-black-primary">{value}</dd>
    </div>
  );
}

function RiskDetailMitigation({
  orgId,
  token,
  riskId,
  riskName,
  analysisRunId,
}: {
  orgId: string;
  token: string;
  riskId: string;
  riskName: string;
  analysisRunId?: string;
}) {
  const [loading, setLoading] = React.useState(true);
  const [plans, setPlans] = React.useState<ReturnType<typeof mapMitigationPlan>[]>([]);
  const [recommendations, setRecommendations] = React.useState<
    ReturnType<typeof mapRecommendation>[]
  >([]);

  React.useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const [planRows, recs] = await Promise.all([
          listRiskMitigationPlans(orgId, token, riskId),
          listRecommendations(orgId, token, { domain_source: "risk", limit: 20 }),
        ]);
        if (cancelled) return;
        const riskMap = new Map([[riskId, riskName]]);
        setPlans(planRows.map((p) => mapMitigationPlan(p, riskMap)));
        setRecommendations(
          recs
            .filter(
              (r) =>
                r.risk_id === riskId ||
                (analysisRunId && r.analysis_run_id === analysisRunId),
            )
            .map(mapRecommendation),
        );
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [orgId, token, riskId, riskName, analysisRunId]);

  return (
    <>
      <section className={executiveSectionSpacingClassName}>
        <DashboardSectionHeader dense title="توصيات التخفيف" />
        {loading ? (
          <LoadingSkeleton className="min-h-[120px] rounded-2xl" />
        ) : recommendations.length === 0 ? (
          <EmptyState title="لا توصيات" description="لا توجد توصيات تنفيذية مرتبطة بهذا الخطر" />
        ) : (
          <div className="grid gap-5 lg:grid-cols-2">
            {recommendations.map((item) => {
              const display = formatRecommendationDisplay(item);
              return (
                <RiskRecommendationCard
                  key={item.id}
                  item={{ ...item, title: display.title, description: display.description }}
                />
              );
            })}
          </div>
        )}
      </section>

      <section className={executiveSectionSpacingClassName}>
        <DashboardSectionHeader dense title="خطط التخفيف" />
        {loading ? (
          <LoadingSkeleton className="min-h-[120px] rounded-2xl" />
        ) : plans.length === 0 ? (
          <EmptyState title="لا خطط" description="لا توجد خطط تخفيف لهذا الخطر" />
        ) : (
          <RiskMitigationPlans plans={plans} />
        )}
      </section>
    </>
  );
}
