export interface DemoArtifacts {
  fileId: string | null;
  snapshotId: string | null;
  snapshotVersion: number | null;
  wasteRunId: string | null;
  aiRecommendationsReady: boolean;
  simulationRunId: string | null;
  lastReportId: string | null;
}

export const DEMO_ARTIFACTS_CHANGED = "khazina:demo-artifacts-changed";

const DEMO_KEY = "khazina_demo_artifacts";

const EMPTY: DemoArtifacts = {
  fileId: null,
  snapshotId: null,
  snapshotVersion: null,
  wasteRunId: null,
  aiRecommendationsReady: false,
  simulationRunId: null,
  lastReportId: null,
};

export function readDemoArtifacts(): DemoArtifacts {
  if (typeof window === "undefined") {
    return EMPTY;
  }
  try {
    const raw = window.sessionStorage.getItem(DEMO_KEY);
    if (!raw) {
      return EMPTY;
    }
    return { ...EMPTY, ...JSON.parse(raw) } as DemoArtifacts;
  } catch {
    return EMPTY;
  }
}

function notifyArtifactsChanged(next: DemoArtifacts): void {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(
    new CustomEvent(DEMO_ARTIFACTS_CHANGED, { detail: next }),
  );
}

export function writeDemoArtifacts(patch: Partial<DemoArtifacts>): DemoArtifacts {
  const next = { ...readDemoArtifacts(), ...patch };
  if (typeof window !== "undefined") {
    window.sessionStorage.setItem(DEMO_KEY, JSON.stringify(next));
    notifyArtifactsChanged(next);
  }
  return next;
}

/** Clears all analysis outputs tied to a prior dataset. */
export function clearAnalysisArtifacts(): DemoArtifacts {
  return writeDemoArtifacts({
    wasteRunId: null,
    aiRecommendationsReady: false,
    simulationRunId: null,
    lastReportId: null,
  });
}

/**
 * Called when a new workbook is ingested — keeps new file/snapshot IDs but
 * drops stale run IDs so pages never show results from a previous upload.
 */
export function beginNewFinancialDataset(patch: {
  fileId: string;
  snapshotId: string;
  snapshotVersion: number;
}): DemoArtifacts {
  return writeDemoArtifacts({
    fileId: patch.fileId,
    snapshotId: patch.snapshotId,
    snapshotVersion: patch.snapshotVersion,
    wasteRunId: null,
    aiRecommendationsReady: false,
    simulationRunId: null,
    lastReportId: null,
  });
}

export function clearDemoArtifacts(): void {
  if (typeof window !== "undefined") {
    window.sessionStorage.removeItem(DEMO_KEY);
    notifyArtifactsChanged(EMPTY);
  }
}
