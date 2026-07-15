export interface DemoArtifacts {
  fileId: string | null;
  snapshotId: string | null;
  snapshotVersion: number | null;
  wasteRunId: string | null;
  simulationRunId: string | null;
  lastReportId: string | null;
}

const DEMO_KEY = "khazina_demo_artifacts";

const EMPTY: DemoArtifacts = {
  fileId: null,
  snapshotId: null,
  snapshotVersion: null,
  wasteRunId: null,
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

export function writeDemoArtifacts(patch: Partial<DemoArtifacts>): DemoArtifacts {
  const next = { ...readDemoArtifacts(), ...patch };
  if (typeof window !== "undefined") {
    window.sessionStorage.setItem(DEMO_KEY, JSON.stringify(next));
  }
  return next;
}

export function clearDemoArtifacts(): void {
  if (typeof window !== "undefined") {
    window.sessionStorage.removeItem(DEMO_KEY);
  }
}
