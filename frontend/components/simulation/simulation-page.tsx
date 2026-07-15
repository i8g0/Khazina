"use client";

import * as React from "react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { SimulationComparisonChart } from "@/components/simulation/simulation-comparison-chart";
import { SimulationScenarioCard } from "@/components/simulation/simulation-scenario-card";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PageHero } from "@/components/ui/page-hero";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavItems,
} from "@/lib/app-nav";
import { organization } from "@/lib/placeholder-data";
import { useRequireAuth, formatApiError } from "@/lib/auth/auth-context";
import {
  executeScenario,
  getForecastSummary,
  listChartPoints,
  listComparisonMetrics,
  listScenarios,
} from "@/lib/api/khazina-api";
import { readDemoArtifacts, writeDemoArtifacts } from "@/lib/demo/state";
import { mapSimulationStatus } from "@/lib/format";

export function SimulationPage() {
  const auth = useRequireAuth();
  const [loading, setLoading] = React.useState(true);
  const [executing, setExecuting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [scenarios, setScenarios] = React.useState<
    { id: string; name: string; description: string; status: string }[]
  >([]);
  const [activeId, setActiveId] = React.useState<string | null>(null);
  const [forecast, setForecast] = React.useState({
    baseline: "—",
    projected: "—",
    delta: "—",
    confidence: "—",
  });
  const [chartPoints, setChartPoints] = React.useState<
    { quarter: string; baseline: number; projected: number }[]
  >([]);
  const [comparisons, setComparisons] = React.useState<
    { name: string; current: string; simulated: string; change: string }[]
  >([]);

  const loadScenarios = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    try {
      const rows = await listScenarios(auth.session.organizationId, auth.session.token);
      setScenarios(rows);
      if (!activeId && rows[0]) {
        setActiveId(rows[0].id);
      }
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session, activeId]);

  React.useEffect(() => {
    if (auth.session) void loadScenarios();
  }, [auth.session, loadScenarios]);

  const loadRunResults = async (runId: string) => {
    if (!auth.session) return;
    const [summary, points, metrics] = await Promise.all([
      getForecastSummary(auth.session.organizationId, auth.session.token, runId),
      listChartPoints(auth.session.organizationId, auth.session.token, runId),
      listComparisonMetrics(auth.session.organizationId, auth.session.token, runId),
    ]);
    if (summary) {
      setForecast({
        baseline: summary.baseline_value,
        projected: summary.projected_value,
        delta: summary.delta_value,
        confidence: summary.confidence_label ?? "—",
      });
    }
    setChartPoints(
      points.map((p) => ({
        quarter: p.quarter_label,
        baseline: p.baseline_amount,
        projected: p.projected_amount,
      })),
    );
    setComparisons(
      metrics.map((m) => ({
        name: m.metric_name,
        current: m.current_value,
        simulated: m.simulated_value,
        change: m.change_value,
      })),
    );
  };

  const runScenario = async () => {
    if (!auth.session || !activeId) return;
    const artifacts = readDemoArtifacts();
    if (!artifacts.fileId || !artifacts.snapshotId || !artifacts.snapshotVersion) {
      setError("ارفع ملفاً وشغّل تحليل الهدر أولاً");
      return;
    }
    setExecuting(true);
    setError(null);
    try {
      const outcome = await executeScenario(
        auth.session.organizationId,
        auth.session.token,
        activeId,
        {
          source_file_id: artifacts.fileId,
          source_snapshot_id: artifacts.snapshotId,
          snapshot_version: artifacts.snapshotVersion,
          baseline_analysis_run_id: artifacts.wasteRunId ?? undefined,
        },
      );
      writeDemoArtifacts({ simulationRunId: outcome.simulation_run.id });
      await loadRunResults(outcome.simulation_run.id);
      setMessage("اكتملت المحاكاة بنجاح");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setExecuting(false);
    }
  };

  React.useEffect(() => {
    const runId = readDemoArtifacts().simulationRunId;
    if (auth.session && runId) {
      void loadRunResults(runId).catch(() => undefined);
    }
  }, [auth.session]);

  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="محاكاة الأعمال"
      subtitle={organization.reportingPeriod}
      activeItemId="simulation"
      sidebarVariant="executive"
      navItems={getAppNavItems()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="محاكاة السيناريوهات"
            description="مقارنة السيناريوهات التشغيلية مقابل خط الأساس من بيانات حقيقية."
            period={organization.reportingPeriod}
          />

          <Button disabled={executing || !activeId} onClick={() => void runScenario()}>
            {executing ? "جاري التنفيذ..." : "تشغيل السيناريو النشط"}
          </Button>

          {message ? <Alert variant="success" title="تم">{message}</Alert> : null}
          {error ? <ErrorState title="خطأ" description={error} onRetry={() => setError(null)} /> : null}

          {loading ? (
            <LoadingSkeleton className="min-h-[240px] rounded-2xl" />
          ) : (
            <section className="grid gap-4 md:grid-cols-3">
              {scenarios.map((scenario) => (
                <SimulationScenarioCard
                  key={scenario.id}
                  scenario={{
                    id: scenario.id,
                    name: scenario.name,
                    description: scenario.description,
                    status: mapSimulationStatus(scenario.status),
                  }}
                  active={scenario.id === activeId}
                  onSelect={() => setActiveId(scenario.id)}
                />
              ))}
            </section>
          )}

          <section className="grid gap-5 sm:grid-cols-3">
            <DashboardStatCard label="الأساس" value={forecast.baseline} hint="خط الأساس" dense />
            <DashboardStatCard label="المتوقع" value={forecast.projected} hint="بعد المحاكاة" dense emphasis />
            <DashboardStatCard label="التغير" value={forecast.delta} hint={forecast.confidence} dense />
          </section>

          {chartPoints.length > 0 ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="مقارنة الفترات" />
              <SimulationComparisonChart data={chartPoints} />
            </section>
          ) : null}

          {comparisons.length > 0 ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="مؤشرات المقارنة" />
              <div className="grid gap-4 md:grid-cols-3">
                {comparisons.map((item) => (
                  <DashboardStatCard
                    key={item.name}
                    label={item.name}
                    value={item.simulated}
                    hint={`${item.current} → ${item.change}`}
                    dense
                  />
                ))}
              </div>
            </section>
          ) : null}
        </div>
      </PageContainer>
    </AppLayout>
  );
}
