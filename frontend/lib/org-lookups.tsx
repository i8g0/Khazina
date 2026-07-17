"use client";

import * as React from "react";
import { useAuth } from "@/lib/auth/auth-context";
import {
  listDepartments,
  listFinancialFiles,
  listReportingPeriods,
} from "@/lib/api/khazina-api";
import { MAX_LIST_LIMIT } from "@/lib/api/pagination";
import type {
  DepartmentResponse,
  FinancialFileResponse,
  ReportingPeriodResponse,
} from "@/lib/api/types";

interface OrgLookupsValue {
  isLoading: boolean;
  departments: DepartmentResponse[];
  files: FinancialFileResponse[];
  activeReportingPeriod: ReportingPeriodResponse | null;
  departmentName: (departmentId: string | null | undefined) => string | null;
  fileName: (fileId: string | null | undefined) => string | null;
  refresh: () => Promise<void>;
}

const OrgLookupsContext = React.createContext<OrgLookupsValue | null>(null);

export function OrgLookupsProvider({ children }: { children: React.ReactNode }) {
  const { session } = useAuth();
  const [isLoading, setIsLoading] = React.useState(false);
  const [departments, setDepartments] = React.useState<DepartmentResponse[]>([]);
  const [files, setFiles] = React.useState<FinancialFileResponse[]>([]);
  const [activeReportingPeriod, setActiveReportingPeriod] =
    React.useState<ReportingPeriodResponse | null>(null);

  const refresh = React.useCallback(async () => {
    if (!session) {
      setDepartments([]);
      setFiles([]);
      setActiveReportingPeriod(null);
      return;
    }
    setIsLoading(true);
    try {
      const [deptRows, fileRows, periodRows] = await Promise.all([
        listDepartments(session.organizationId, session.token, {
          limit: MAX_LIST_LIMIT,
          active_only: true,
        }),
        listFinancialFiles(session.organizationId, session.token),
        listReportingPeriods(session.organizationId, session.token, {
          limit: MAX_LIST_LIMIT,
        }),
      ]);
      setDepartments(deptRows);
      setFiles(fileRows);
      const activePeriod = periodRows.find((period) => period.is_active);
      if (activePeriod) {
        setActiveReportingPeriod(activePeriod);
      } else if (periodRows.length > 0) {
        const latest = [...periodRows].sort(
          (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
        )[0];
        setActiveReportingPeriod(latest);
      } else {
        setActiveReportingPeriod(null);
      }
    } finally {
      setIsLoading(false);
    }
  }, [session]);

  React.useEffect(() => {
    void refresh();
  }, [refresh]);

  const departmentName = React.useCallback(
    (departmentId: string | null | undefined) => {
      if (!departmentId) return null;
      return departments.find((dept) => dept.id === departmentId)?.name_ar ?? null;
    },
    [departments],
  );

  const fileName = React.useCallback(
    (fileId: string | null | undefined) => {
      if (!fileId) return null;
      return files.find((file) => file.id === fileId)?.file_name ?? null;
    },
    [files],
  );

  const value = React.useMemo(
    () => ({
      isLoading,
      departments,
      files,
      activeReportingPeriod,
      departmentName,
      fileName,
      refresh,
    }),
    [
      isLoading,
      departments,
      files,
      activeReportingPeriod,
      departmentName,
      fileName,
      refresh,
    ],
  );

  return (
    <OrgLookupsContext.Provider value={value}>
      {children}
    </OrgLookupsContext.Provider>
  );
}

export function useOrgLookups(): OrgLookupsValue {
  const value = React.useContext(OrgLookupsContext);
  if (!value) {
    throw new Error("useOrgLookups must be used within OrgLookupsProvider");
  }
  return value;
}

export function useOrganizationDisplay() {
  const { session } = useAuth();
  const { activeReportingPeriod } = useOrgLookups();
  return {
    name: session?.organizationName ?? "خزينة",
    platformName: session?.platformName ?? "خزينة",
    executiveTitle: session?.executiveTitle ?? "المستخدم التنفيذي",
    reportingPeriod: activeReportingPeriod?.label ?? null,
  };
}
