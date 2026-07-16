"use client";

import * as React from "react";
import {
  DEMO_ARTIFACTS_CHANGED,
  readDemoArtifacts,
  type DemoArtifacts,
} from "@/lib/demo/state";

export function useDemoArtifacts(): DemoArtifacts {
  const [artifacts, setArtifacts] = React.useState<DemoArtifacts>(EMPTY);

  React.useEffect(() => {
    setArtifacts(readDemoArtifacts());
    const handler = () => setArtifacts(readDemoArtifacts());
    window.addEventListener(DEMO_ARTIFACTS_CHANGED, handler);
    return () => window.removeEventListener(DEMO_ARTIFACTS_CHANGED, handler);
  }, []);

  return artifacts;
}

const EMPTY: DemoArtifacts = {
  fileId: null,
  snapshotId: null,
  snapshotVersion: null,
  wasteRunId: null,
  aiRecommendationsReady: false,
  riskRunId: null,
  riskAiReady: false,
  simulationRunId: null,
  simulationAnalysisRunId: null,
  lastReportId: null,
};
