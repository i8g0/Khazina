"use client";

import * as React from "react";
import { Play, Plus } from "lucide-react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardRecommendationCard } from "@/components/dashboard/dashboard-recommendation-card";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { SimulationActionPanel } from "@/components/simulation/simulation-action-panel";
import { SimulationAssumptions } from "@/components/simulation/simulation-assumptions";
import { SimulationComparisonChart } from "@/components/simulation/simulation-comparison-chart";
import { SimulationImpactBreakdown } from "@/components/simulation/simulation-impact-breakdown";
import { SimulationResultsSummary } from "@/components/simulation/simulation-results-summary";
import { SimulationScenarioCard } from "@/components/simulation/simulation-scenario-card";
import { Button } from "@/components/ui/button";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { PageHero } from "@/components/ui/page-hero";
import { executivePageContainerClassName, executivePageSpacingClassName, executiveSectionSpacingClassName, getAppNavItems } from "@/lib/app-nav";
import {
  organization,
  simulationActionItems,
  simulationAssumptions,
  simulationChartSeries,
  simulationComparisonMetrics,
  simulationForecasts,
  simulationImpactBreakdown,
  simulationRecommendations,
  simulationResultSummaries,
  simulationScenarios,
} from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

type SimulationViewState = "idle" | "loading" | "ready";

const LOADING_MS = 1400;

function changeTone(direction: "up" | "down" | "neutral") {
  if (direction === "up") {
    return "text-warning";
  }
  if (direction === "down") {
    return "text-success";
  }
  return "text-muted";
}

export function SimulationPage() {
  const [activeScenarioId, setActiveScenarioId] = React.useState(
    simulationScenarios[0]?.id ?? "",
  );
  const [viewState, setViewState] = React.useState<SimulationViewState>("idle");

  const activeForecast = React.useMemo(
    () => simulationForecasts.find((item) => item.scenarioId === activeScenarioId),
    [activeScenarioId],
  );

  const runSimulation = React.useCallback(() => {
    setViewState("loading");
    window.setTimeout(() => {
      setViewState("ready");
    }, LOADING_MS);
  }, []);

  const handleScenarioSelect = React.useCallback((scenarioId: string) => {
    setActiveScenarioId(scenarioId);
    setViewState("idle");
  }, []);

  const assumptions = simulationAssumptions[activeScenarioId] ?? [];
  const chartData = simulationChartSeries[activeScenarioId] ?? [];
  const comparisonMetrics = simulationComparisonMetrics[activeScenarioId] ?? [];
  const impactItems = simulationImpactBreakdown[activeScenarioId] ?? [];
  const resultSummary = simulationResultSummaries[activeScenarioId];

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="محاكاة الأعمال"
      subtitle={organization.reportingPeriod}
      activeItemId="simulation"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div
          className={cn(
            viewState === "ready"
              ? executivePageSpacingClassName
              : "space-y-6 md:space-y-8",
          )}
        >
          <PageHero
            title="محاكاة الأعمال"
            description="بناء ومقارنة سيناريوهات مالية افتراضية لدعم القرارات التنفيذية."
            period={organization.reportingPeriod}
            actions={
              <Button variant="secondary" disabled>
                <Plus className="h-4 w-4" strokeWidth={1.75} />
                سيناريو جديد
              </Button>
            }
          />

          <section className={executiveSectionSpacingClassName}>
            <DashboardSectionHeader
              dense
              title="اختيار السيناريو"
              description="اختر سيناريو للمحاكاة — حتى 3 سيناريوهات متاحة"
            />
            <div
              role="listbox"
              aria-label="سيناريوهات المحاكاة"
              className="grid gap-5 md:grid-cols-2 xl:grid-cols-3 xl:gap-5"
            >
              {simulationScenarios.map((scenario) => (
                <SimulationScenarioCard
                  key={scenario.id}
                  scenario={scenario}
                  active={scenario.id === activeScenarioId}
                  onSelect={() => handleScenarioSelect(scenario.id)}
                />
              ))}
            </div>
          </section>

          <section className={executiveSectionSpacingClassName}>
            <SimulationAssumptions assumptions={assumptions} />
          </section>

          <section className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-muted">
              {viewState === "ready"
                ? "تمت المحاكاة — يمكنك إعادة التشغيل بعد تغيير السيناريو"
                : "اضغط لتشغيل المحاكاة وعرض النتائج"}
            </p>
            <Button
              onClick={runSimulation}
              disabled={viewState === "loading" || !activeScenarioId}
            >
              {viewState === "loading" ? (
                <>
                  <LoadingSpinner size="sm" />
                  جاري المحاكاة...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" strokeWidth={1.75} />
                  تشغيل المحاكاة
                </>
              )}
            </Button>
          </section>

          {viewState === "loading" ? (
            <div className="space-y-8">
              <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 3 }).map((_, index) => (
                  <LoadingSkeleton key={index} className="min-h-[188px] rounded-2xl" />
                ))}
              </div>
              <LoadingSkeleton className="min-h-[460px] rounded-2xl" />
              <LoadingSkeleton className="min-h-[320px] rounded-2xl" />
            </div>
          ) : null}

          {viewState === "ready" && activeForecast && resultSummary ? (
            <>
              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader
                  dense
                  title="ملخص النتائج"
                  description="مؤشرات التوقع للسيناريو النشط"
                />
                <SimulationResultsSummary
                  forecast={activeForecast}
                  summary={resultSummary}
                />
              </section>

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader
                  dense
                  title="مقارنة الأداء"
                  description="مؤشرات رئيسية — الوضع الحالي مقابل المحاكاة"
                />
                <div className="grid gap-5 lg:grid-cols-3 lg:gap-5">
                  {comparisonMetrics.map((metric) => (
                    <article
                      key={metric.metric}
                      className="rounded-2xl border border-border/60 bg-surface px-5 py-5 md:px-6 md:py-5"
                    >
                      <h3 className="mb-4 text-sm font-semibold text-black-primary">
                        {metric.metric}
                      </h3>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-muted">
                            الحالي
                          </p>
                          <p className="text-lg font-semibold tabular-nums text-black-primary">
                            {metric.current}
                          </p>
                        </div>
                        <div>
                          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-muted">
                            المحاكاة
                          </p>
                          <p className="text-lg font-semibold tabular-nums text-black-primary">
                            {metric.simulated}
                          </p>
                        </div>
                      </div>
                      <p
                        className={cn(
                          "mt-4 text-sm font-semibold tabular-nums",
                          changeTone(metric.direction),
                        )}
                      >
                        التغير: {metric.change}
                      </p>
                    </article>
                  ))}
                </div>
              </section>

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader
                  dense
                  title="مخطط المقارنة"
                  description="الأساس مقابل المتوقع عبر الأرباع"
                />
                <SimulationComparisonChart data={chartData} />
              </section>

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader
                  dense
                  title="تفصيل الأثر المالي"
                  description="توزيع الأثر حسب الفئات والإدارات"
                />
                <SimulationImpactBreakdown items={impactItems} />
              </section>

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader
                  dense
                  title="توصيات الذكاء الاصطناعي"
                  description="إجراءات مقترحة بناءً على نتائج المحاكاة"
                />
                <div className="grid gap-5 lg:grid-cols-3 lg:gap-5">
                  {simulationRecommendations.map((item) => (
                    <DashboardRecommendationCard
                      key={item.id}
                      id={item.id}
                      title={item.title}
                      description={item.description}
                      badge={item.badge}
                      confidence={item.confidence}
                    />
                  ))}
                </div>
              </section>

              <section className={executiveSectionSpacingClassName}>
                <DashboardSectionHeader
                  dense
                  title="ملخص الإجراءات"
                  description="الخطوات المقترحة بعد مراجعة نتائج المحاكاة"
                />
                <SimulationActionPanel items={simulationActionItems} />
              </section>
            </>
          ) : null}
        </div>
      </PageContainer>
    </AppLayout>
  );
}
