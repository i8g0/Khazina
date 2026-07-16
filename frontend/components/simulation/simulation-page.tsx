"use client";

import * as React from "react";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DashboardStatCard } from "@/components/dashboard/dashboard-stat-card";
import { SimulationActionPanel } from "@/components/simulation/simulation-action-panel";
import { SimulationAssumptions } from "@/components/simulation/simulation-assumptions";
import { SimulationComparisonChart } from "@/components/simulation/simulation-comparison-chart";
import { SimulationImpactBreakdown } from "@/components/simulation/simulation-impact-breakdown";
import { SimulationScenarioCard } from "@/components/simulation/simulation-scenario-card";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Input } from "@/components/ui/input";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PageHero } from "@/components/ui/page-hero";
import Link from "next/link";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavGroups,
  navRouteMap,
} from "@/lib/app-nav";
import { WorkflowIndicator } from "@/components/workflow/workflow-indicator";
import { OperationLoadingPanel } from "@/components/workflow/operation-loading-panel";
import { AuthLoadingShell } from "@/components/workflow/auth-loading-shell";
import { EXECUTIVE_MESSAGES } from "@/lib/workflow/messages";
import {
  useRequireAuth,
  formatApiError,
} from "@/lib/auth/auth-context";
import { useOrganizationDisplay } from "@/lib/org-lookups";
import {
  createScenario,
  executeScenario,
  getForecastSummary,
  listActionItems,
  listChartPoints,
  listComparisonMetrics,
  listImpactItems,
  listScenarioAssumptions,
  listScenarios,
} from "@/lib/api/khazina-api";
import { writeDemoArtifacts } from "@/lib/demo/state";
import { useDemoArtifacts } from "@/lib/demo/hooks";
import { mapSimulationStatus } from "@/lib/format";

function mapImpactDirection(
  direction: string,
): "up" | "down" | "neutral" {
  if (direction === "up" || direction === "down") {
    return direction;
  }
  return "neutral";
}

export function SimulationPage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const artifacts = useDemoArtifacts();
  const [loading, setLoading] = React.useState(true);
  const [executing, setExecuting] = React.useState(false);
  const [creating, setCreating] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [newName, setNewName] = React.useState("");
  const [newDescription, setNewDescription] = React.useState("");
  const [scenarios, setScenarios] = React.useState<
    { id: string; name: string; description: string; status: string }[]
  >([]);
  const [activeId, setActiveId] = React.useState<string | null>(null);
  const [assumptions, setAssumptions] = React.useState<
    { id: string; label: string; value: string }[]
  >([]);
  const [hasRunResults, setHasRunResults] = React.useState(false);
  const [forecast, setForecast] = React.useState<{
    baseline: string;
    projected: string;
    delta: string;
    confidence: string | null;
  } | null>(null);
  const [chartPoints, setChartPoints] = React.useState<
    { quarter: string; baseline: number; projected: number }[]
  >([]);
  const [comparisons, setComparisons] = React.useState<
    { name: string; current: string; simulated: string; change: string }[]
  >([]);
  const [impactItems, setImpactItems] = React.useState<
    {
      id: string;
      category: string;
      baseline: string;
      projected: string;
      change: string;
      direction: "up" | "down" | "neutral";
    }[]
  >([]);
  const [actionItems, setActionItems] = React.useState<
    { id: string; title: string; description: string; status: string }[]
  >([]);

  const loadScenarios = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    try {
      const rows = await listScenarios(
        auth.session.organizationId,
        auth.session.token,
      );
      setScenarios(rows);
      setActiveId((current) => {
        if (current && rows.some((row) => row.id === current)) {
          return current;
        }
        return rows[0]?.id ?? null;
      });
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session]);

  React.useEffect(() => {
    if (auth.session) void loadScenarios();
  }, [auth.session, loadScenarios]);

  const loadAssumptions = React.useCallback(
    async (scenarioId: string) => {
      if (!auth.session) return;
      try {
        const rows = await listScenarioAssumptions(
          auth.session.organizationId,
          auth.session.token,
          scenarioId,
        );
        setAssumptions(
          rows.map((item) => ({
            id: item.id,
            label: item.label,
            value: item.value,
          })),
        );
      } catch {
        setAssumptions([]);
      }
    },
    [auth.session],
  );

  React.useEffect(() => {
    if (activeId) {
      void loadAssumptions(activeId);
    } else {
      setAssumptions([]);
    }
  }, [activeId, loadAssumptions]);

  const loadRunResults = async (runId: string) => {
    if (!auth.session) return;
    const [summary, points, metrics, impacts, actions] = await Promise.all([
      getForecastSummary(auth.session.organizationId, auth.session.token, runId),
      listChartPoints(auth.session.organizationId, auth.session.token, runId),
      listComparisonMetrics(
        auth.session.organizationId,
        auth.session.token,
        runId,
      ),
      listImpactItems(auth.session.organizationId, auth.session.token, runId),
      listActionItems(auth.session.organizationId, auth.session.token, runId),
    ]);
    if (summary) {
      setForecast({
        baseline: summary.baseline_value,
        projected: summary.projected_value,
        delta: summary.delta_value,
        confidence: summary.confidence_label,
      });
      setHasRunResults(true);
    } else {
      setForecast(null);
      setHasRunResults(false);
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
    setImpactItems(
      impacts.map((item) => ({
        id: item.id,
        category: item.category_label,
        baseline: item.baseline_value,
        projected: item.projected_value,
        change: item.change_value,
        direction: mapImpactDirection(item.direction),
      })),
    );
    setActionItems(
      actions.map((item) => ({
        id: item.id,
        title: item.title,
        description: item.description,
        status: item.status,
      })),
    );
  };

  const handleCreate = async () => {
    if (!auth.session) return;
    const name = newName.trim();
    const description = newDescription.trim();
    if (!name || !description) {
      setError("أدخل اسم السيناريو ووصفه");
      return;
    }
    setCreating(true);
    setError(null);
    try {
      const created = await createScenario(
        auth.session.organizationId,
        auth.session.token,
        { name, description },
      );
      setNewName("");
      setNewDescription("");
      setActiveId(created.id);
      setMessage("تم إنشاء السيناريو");
      await loadScenarios();
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setCreating(false);
    }
  };

  const resetRunResults = React.useCallback(() => {
    setHasRunResults(false);
    setForecast(null);
    setChartPoints([]);
    setComparisons([]);
    setImpactItems([]);
    setActionItems([]);
  }, []);

  const runScenario = async () => {
    if (!auth.session || !activeId) return;
    if (!artifacts.fileId || !artifacts.snapshotId || !artifacts.snapshotVersion) {
      setError("ارفع ملفاً وشغّل تحليل الهدر أولاً");
      return;
    }
    setExecuting(true);
    setError(null);
    try {
      const scenarioBody: {
        source_file_id: string;
        source_snapshot_id?: string;
        snapshot_version?: number;
        baseline_analysis_run_id?: string;
      } = {
        source_file_id: artifacts.fileId,
        baseline_analysis_run_id: artifacts.wasteRunId ?? undefined,
      };
      if (artifacts.snapshotId) {
        scenarioBody.source_snapshot_id = artifacts.snapshotId;
      } else if (artifacts.snapshotVersion) {
        scenarioBody.snapshot_version = artifacts.snapshotVersion;
      }
      const outcome = await executeScenario(
        auth.session.organizationId,
        auth.session.token,
        activeId,
        scenarioBody,
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
    if (!auth.session) return;
    if (!artifacts.simulationRunId) {
      resetRunResults();
      return;
    }
    void loadRunResults(artifacts.simulationRunId).catch(() => undefined);
  }, [auth.session, artifacts.simulationRunId, resetRunResults]);

  if (auth.isLoading) return <AuthLoadingShell />;
  if (!auth.session) return null;

  const activeScenario = scenarios.find((scenario) => scenario.id === activeId);

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="محاكاة الأعمال"
      subtitle={org.reportingPeriod ?? undefined}
      activeItemId="simulation"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="محاكاة السيناريوهات"
            description="مقارنة السيناريوهات التشغيلية مقابل خط الأساس من بيانات حقيقية."
            period={org.reportingPeriod}
          />

          <WorkflowIndicator activeStageId="simulation" />

          <Alert variant="default" title="إرشاد">
            {EXECUTIVE_MESSAGES.simulationDemoHint}
          </Alert>

          <div className="flex flex-wrap items-end gap-3">
            <div className="min-w-[200px] flex-1 space-y-1.5">
              <label className="text-sm text-muted">اسم السيناريو</label>
              <Input
                value={newName}
                onChange={(event) => setNewName(event.target.value)}
                placeholder="مثال: خفض المشتريات 10%"
              />
            </div>
            <div className="min-w-[260px] flex-[2] space-y-1.5">
              <label className="text-sm text-muted">الوصف</label>
              <Input
                value={newDescription}
                onChange={(event) => setNewDescription(event.target.value)}
                placeholder="وصف مختصر للسيناريو"
              />
            </div>
            <Button
              variant="secondary"
              disabled={creating}
              onClick={() => void handleCreate()}
            >
              {creating ? "جاري الإنشاء..." : "إنشاء سيناريو"}
            </Button>
            <Button
              disabled={executing || !activeId}
              onClick={() => void runScenario()}
            >
              {executing
                ? "جاري التنفيذ..."
                : activeScenario
                  ? `تشغيل: ${activeScenario.name}`
                  : "تشغيل السيناريو"}
            </Button>
            {hasRunResults ? (
              <Button asChild variant="secondary">
                <Link href={navRouteMap.reports}>التالي: إنشاء التقرير</Link>
              </Button>
            ) : null}
          </div>

          {executing ? (
            <OperationLoadingPanel
              title="جاري تشغيل محاكاة السيناريو"
              description="حساب التوقعات والمقارنات بناءً على نتائج تحليل الهدر."
            />
          ) : null}

          {message ? <Alert variant="success" title="تم">{message}</Alert> : null}
          {error ? (
            <ErrorState
              title="تعذّر تشغيل المحاكاة"
              description={error}
              onRetry={() => setError(null)}
            />
          ) : null}

          {loading ? (
            <LoadingSkeleton className="min-h-[240px] rounded-2xl" />
          ) : scenarios.length === 0 ? (
            <EmptyState
              title="لا توجد سيناريوهات"
              description="أنشئ سيناريوًا جديدًا للبدء."
            />
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

          {activeId ? (
            assumptions.length > 0 ? (
              <SimulationAssumptions
                assumptions={assumptions.map(({ label, value }) => ({ label, value }))}
              />
            ) : (
              <EmptyState
                title="لا توجد افتراضات مسجّلة"
                description="لم يُعرّف هذا السيناريو أي افتراضات بعد."
              />
            )
          ) : null}

          {hasRunResults && forecast ? (
            <section className="grid gap-5 sm:grid-cols-3">
              <DashboardStatCard
                label="الأساس"
                value={forecast.baseline}
                hint="خط الأساس"
                dense
              />
              <DashboardStatCard
                label="المتوقع"
                value={forecast.projected}
                hint="بعد المحاكاة"
                dense
                emphasis
              />
              <DashboardStatCard
                label="التغير"
                value={forecast.delta}
                hint={forecast.confidence ?? "بدون تصنيف ثقة"}
                dense
              />
            </section>
          ) : (
            <EmptyState
              title="لا توجد نتائج محاكاة بعد"
              description="شغّل السيناريو النشط لعرض ملخص التوقعات والمقارنات."
            />
          )}

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

          {impactItems.length > 0 ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="تأثير المحاكاة حسب الفئة" />
              <SimulationImpactBreakdown items={impactItems} />
            </section>
          ) : null}

          {actionItems.length > 0 ? (
            <section className={executiveSectionSpacingClassName}>
              <DashboardSectionHeader dense title="إجراءات مقترحة" />
              <SimulationActionPanel items={actionItems} />
            </section>
          ) : null}
        </div>
      </PageContainer>
    </AppLayout>
  );
}
