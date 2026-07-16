"use client";

import * as React from "react";
import Link from "next/link";
import { AppLayout, PageContainer } from "@/components/layout";
import { DashboardBrand } from "@/components/dashboard/dashboard-brand";
import { DashboardSectionHeader } from "@/components/dashboard/dashboard-section-header";
import { DemoHeaderActions } from "@/components/notifications/notification-bell";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ErrorState } from "@/components/ui/error-state";
import { Input } from "@/components/ui/input";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PageHero } from "@/components/ui/page-hero";
import {
  executivePageContainerClassName,
  executivePageSpacingClassName,
  executiveSectionSpacingClassName,
  getAppNavGroups,
} from "@/lib/app-nav";
import {
  getOrganizationSettings,
  patchOrganizationSettings,
} from "@/lib/api/khazina-api";
import type {
  ResolvedSettingsResponse,
  SettingsPatchPayload,
} from "@/lib/api/types";
import {
  formatApiError,
  useOrganizationDisplay,
  useRequireAuth,
} from "@/lib/auth/auth-context";
import { AuthLoadingShell } from "@/components/workflow/auth-loading-shell";

type DraftState = {
  organization_settings: ResolvedSettingsResponse["organization_settings"];
  localization: Pick<
    ResolvedSettingsResponse["localization"],
    "prompt_language" | "report_language"
  >;
  ai_configuration: ResolvedSettingsResponse["ai_configuration"];
  analysis_configuration: ResolvedSettingsResponse["analysis_configuration"];
  report_preferences: ResolvedSettingsResponse["report_preferences"];
  platform_default_notification_preferences: ResolvedSettingsResponse["platform_default_notification_preferences"];
};

function toDraft(settings: ResolvedSettingsResponse): DraftState {
  return {
    organization_settings: { ...settings.organization_settings },
    localization: {
      prompt_language: settings.localization.prompt_language,
      report_language: settings.localization.report_language,
    },
    ai_configuration: { ...settings.ai_configuration },
    analysis_configuration: {
      ...settings.analysis_configuration,
      enabled_analysis_types: [
        ...settings.analysis_configuration.enabled_analysis_types,
      ],
    },
    report_preferences: { ...settings.report_preferences },
    platform_default_notification_preferences: {
      ...settings.platform_default_notification_preferences,
      enabled_notification_kinds: [
        ...settings.platform_default_notification_preferences
          .enabled_notification_kinds,
      ],
    },
  };
}

export function SettingsPage() {
  const auth = useRequireAuth();
  const org = useOrganizationDisplay();
  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [documentVersion, setDocumentVersion] = React.useState<string>("—");
  const [identity, setIdentity] = React.useState<
    ResolvedSettingsResponse["organization_identity"] | null
  >(null);
  const [localizationSources, setLocalizationSources] = React.useState({
    prompt_language_source: "—",
    report_language_source: "—",
  });
  const [draft, setDraft] = React.useState<DraftState | null>(null);

  const load = React.useCallback(async () => {
    if (!auth.session) return;
    setLoading(true);
    setError(null);
    try {
      const settings = await getOrganizationSettings(
        auth.session.organizationId,
        auth.session.token,
      );
      setDocumentVersion(settings.document_version);
      setIdentity(settings.organization_identity);
      setLocalizationSources({
        prompt_language_source: settings.localization.prompt_language_source,
        report_language_source: settings.localization.report_language_source,
      });
      setDraft(toDraft(settings));
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [auth.session]);

  React.useEffect(() => {
    if (auth.session) void load();
  }, [auth.session, load]);

  const save = async () => {
    if (!auth.session || !draft) return;
    setSaving(true);
    setError(null);
    setMessage(null);
    const payload: SettingsPatchPayload = {
      organization_settings: draft.organization_settings,
      localization: draft.localization,
      ai_configuration: draft.ai_configuration,
      analysis_configuration: draft.analysis_configuration,
      report_preferences: draft.report_preferences,
      platform_default_notification_preferences:
        draft.platform_default_notification_preferences,
    };
    try {
      const updated = await patchOrganizationSettings(
        auth.session.organizationId,
        auth.session.token,
        payload,
      );
      setDocumentVersion(updated.document_version);
      setIdentity(updated.organization_identity);
      setDraft(toDraft(updated));
      setMessage("تم حفظ إعدادات المؤسسة");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSaving(false);
    }
  };

  if (auth.isLoading) return <AuthLoadingShell />;
  if (!auth.session) return null;

  return (
    <AppLayout
      brand={<DashboardBrand />}
      title="الإعدادات"
      subtitle={org.reportingPeriod}
      activeItemId="settings"
      sidebarVariant="executive"
      navGroups={getAppNavGroups()}
      headerActions={<DemoHeaderActions />}
    >
      <PageContainer className={executivePageContainerClassName}>
        <div className={executivePageSpacingClassName}>
          <PageHero
            title="إعدادات المؤسسة"
            description="ضبط الهوية، اللغات، التوصيات، التحليلات، التقارير، والإشعارات."
            period={org.reportingPeriod}
          />

          <div className="flex flex-wrap items-center gap-3">
            <Button disabled={saving || loading || !draft} onClick={() => void save()}>
              {saving ? "جاري الحفظ..." : "حفظ التغييرات"}
            </Button>
            <Button
              variant="secondary"
              disabled={loading || saving}
              onClick={() => void load()}
            >
              إعادة التحميل
            </Button>
            <p className="text-sm text-muted">
              إصدار المستند: {documentVersion}
            </p>
          </div>

          {message ? <Alert variant="success" title="تم">{message}</Alert> : null}
          {error ? (
            <ErrorState
              title="خطأ"
              description={error}
              onRetry={() => void load()}
            />
          ) : null}

          {loading || !draft ? (
            <LoadingSkeleton className="min-h-[480px] rounded-2xl" />
          ) : (
            <div className={executiveSectionSpacingClassName}>
              <SettingsSection title="هوية المؤسسة (عرض فقط)">
                <ReadOnlyRow label="الاسم" value={identity?.name ?? "—"} />
                <ReadOnlyRow
                  label="المنصة"
                  value={identity?.platform_name ?? "—"}
                />
                <ReadOnlyRow
                  label="المسمى التنفيذي"
                  value={identity?.executive_title ?? "—"}
                />
                <p className="text-sm text-muted md:col-span-2">
                  تعديل الهوية عبر{" "}
                  <Link href="/organization" className="text-gold-dark underline">
                    إدارة المؤسسة
                  </Link>
                  .
                </p>
              </SettingsSection>

              <SettingsSection title="1 — إعدادات المؤسسة">
                <Field
                  label="اللغة المحلية"
                  value={draft.organization_settings.locale}
                  onChange={(value) =>
                    setDraft({
                      ...draft,
                      organization_settings: {
                        ...draft.organization_settings,
                        locale: value,
                      },
                    })
                  }
                />
                <Field
                  label="صيغة التاريخ"
                  value={draft.organization_settings.date_display_format}
                  onChange={(value) =>
                    setDraft({
                      ...draft,
                      organization_settings: {
                        ...draft.organization_settings,
                        date_display_format: value,
                      },
                    })
                  }
                />
                <Field
                  label="رمز العملة"
                  value={draft.organization_settings.currency_display_code}
                  onChange={(value) =>
                    setDraft({
                      ...draft,
                      organization_settings: {
                        ...draft.organization_settings,
                        currency_display_code: value,
                      },
                    })
                  }
                />
              </SettingsSection>

              <SettingsSection title="2 — التوطين">
                <Field
                  label="لغة الأوامر"
                  value={draft.localization.prompt_language}
                  onChange={(value) =>
                    setDraft({
                      ...draft,
                      localization: {
                        ...draft.localization,
                        prompt_language: value,
                      },
                    })
                  }
                />
                <Field
                  label="لغة التقارير"
                  value={draft.localization.report_language}
                  onChange={(value) =>
                    setDraft({
                      ...draft,
                      localization: {
                        ...draft.localization,
                        report_language: value,
                      },
                    })
                  }
                />
                <ReadOnlyRow
                  label="مصدر لغة الأوامر"
                  value={localizationSources.prompt_language_source}
                />
                <ReadOnlyRow
                  label="مصدر لغة التقارير"
                  value={localizationSources.report_language_source}
                />
              </SettingsSection>

              <SettingsSection title="التوصيات الذكية">
                <Toggle
                  label="تفعيل التوصيات التنفيذية"
                  checked={draft.ai_configuration.ai_recommendations_enabled}
                  onChange={(checked) =>
                    setDraft({
                      ...draft,
                      ai_configuration: {
                        ...draft.ai_configuration,
                        ai_recommendations_enabled: checked,
                      },
                    })
                  }
                />
                <Toggle
                  label="اقتراح تلقائي لتوصيات الهدر"
                  checked={
                    draft.ai_configuration.waste_recommendations_auto_suggest
                  }
                  onChange={(checked) =>
                    setDraft({
                      ...draft,
                      ai_configuration: {
                        ...draft.ai_configuration,
                        waste_recommendations_auto_suggest: checked,
                      },
                    })
                  }
                />
              </SettingsSection>

              <SettingsSection title="4 — تكوين التحليل">
                <Field
                  label="أنواع التحليل المفعلة (مفصولة بفاصلة)"
                  value={draft.analysis_configuration.enabled_analysis_types.join(
                    ", ",
                  )}
                  onChange={(value) =>
                    setDraft({
                      ...draft,
                      analysis_configuration: {
                        ...draft.analysis_configuration,
                        enabled_analysis_types: value
                          .split(",")
                          .map((part) => part.trim())
                          .filter(Boolean),
                      },
                    })
                  }
                />
                <Field
                  label="قالب عنوان التحليل"
                  value={
                    draft.analysis_configuration.default_analysis_title_template
                  }
                  onChange={(value) =>
                    setDraft({
                      ...draft,
                      analysis_configuration: {
                        ...draft.analysis_configuration,
                        default_analysis_title_template: value,
                      },
                    })
                  }
                />
                <Toggle
                  label="إضافة حدث للخط الزمني عند اكتمال التحليل"
                  checked={
                    draft.analysis_configuration.timeline_on_completion_enabled
                  }
                  onChange={(checked) =>
                    setDraft({
                      ...draft,
                      analysis_configuration: {
                        ...draft.analysis_configuration,
                        timeline_on_completion_enabled: checked,
                      },
                    })
                  }
                />
                <Toggle
                  label="اشتراط التوصيات قبل التقرير"
                  checked={
                    draft.analysis_configuration.require_ai_insights_before_report
                  }
                  onChange={(checked) =>
                    setDraft({
                      ...draft,
                      analysis_configuration: {
                        ...draft.analysis_configuration,
                        require_ai_insights_before_report: checked,
                      },
                    })
                  }
                />
              </SettingsSection>

              <SettingsSection title="5 — تفضيلات التقارير">
                <Field
                  label="قالب عنوان التقرير"
                  value={
                    draft.report_preferences.default_report_title_template
                  }
                  onChange={(value) =>
                    setDraft({
                      ...draft,
                      report_preferences: {
                        ...draft.report_preferences,
                        default_report_title_template: value,
                      },
                    })
                  }
                />
                <Toggle
                  label="نشر تلقائي عند الإنشاء"
                  checked={draft.report_preferences.auto_publish_on_generate}
                  onChange={(checked) =>
                    setDraft({
                      ...draft,
                      report_preferences: {
                        ...draft.report_preferences,
                        auto_publish_on_generate: checked,
                      },
                    })
                  }
                />
                <Toggle
                  label="تضمين ملخص التوصيات عند التوفر"
                  checked={
                    draft.report_preferences.include_ai_sections_when_available
                  }
                  onChange={(checked) =>
                    setDraft({
                      ...draft,
                      report_preferences: {
                        ...draft.report_preferences,
                        include_ai_sections_when_available: checked,
                      },
                    })
                  }
                />
                <Toggle
                  label="تضمين قسم التوصيات"
                  checked={
                    draft.report_preferences.include_recommendations_section
                  }
                  onChange={(checked) =>
                    setDraft({
                      ...draft,
                      report_preferences: {
                        ...draft.report_preferences,
                        include_recommendations_section: checked,
                      },
                    })
                  }
                />
                <Toggle
                  label="تضمين قسم مصدر السيناريو"
                  checked={
                    draft.report_preferences.include_scenario_provenance_section
                  }
                  onChange={(checked) =>
                    setDraft({
                      ...draft,
                      report_preferences: {
                        ...draft.report_preferences,
                        include_scenario_provenance_section: checked,
                      },
                    })
                  }
                />
              </SettingsSection>

              <SettingsSection title="6 — تفضيلات الإشعارات الافتراضية">
                <Toggle
                  label="تفعيل الإشعارات"
                  checked={
                    draft.platform_default_notification_preferences
                      .notifications_enabled
                  }
                  onChange={(checked) =>
                    setDraft({
                      ...draft,
                      platform_default_notification_preferences: {
                        ...draft.platform_default_notification_preferences,
                        notifications_enabled: checked,
                      },
                    })
                  }
                />
                <Field
                  label="أنواع الإشعارات المفعلة (مفصولة بفاصلة)"
                  value={draft.platform_default_notification_preferences.enabled_notification_kinds.join(
                    ", ",
                  )}
                  onChange={(value) =>
                    setDraft({
                      ...draft,
                      platform_default_notification_preferences: {
                        ...draft.platform_default_notification_preferences,
                        enabled_notification_kinds: value
                          .split(",")
                          .map((part) => part.trim())
                          .filter(Boolean),
                      },
                    })
                  }
                />
              </SettingsSection>
            </div>
          )}
        </div>
      </PageContainer>
    </AppLayout>
  );
}

function SettingsSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className={executiveSectionSpacingClassName}>
      <DashboardSectionHeader dense title={title} />
      <Card className="shadow-soft hover:shadow-soft">
        <CardHeader className="pb-2">
          <CardTitle className="sr-only">{title}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">{children}</CardContent>
      </Card>
    </section>
  );
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="space-y-1.5 text-sm">
      <span className="text-muted">{label}</span>
      <Input value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function Toggle({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-3 text-sm text-black-primary">
      <input
        type="checkbox"
        className="h-4 w-4 accent-[var(--gold-primary,#b8860b)]"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
      />
      <span>{label}</span>
    </label>
  );
}

function ReadOnlyRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="space-y-1 text-sm">
      <p className="text-muted">{label}</p>
      <p className="font-medium text-black-primary">{value}</p>
    </div>
  );
}
