export type ExecutiveHealthLevel =
  | "excellent"
  | "good"
  | "needs_attention"
  | "critical";

export interface ExecutiveIndicator {
  id: string;
  label: string;
  value: string | null;
  hint?: string;
  href: string;
  emptyMessage: string;
}

export interface ExecutiveAlert {
  id: string;
  title: string;
  description: string;
  href: string;
  severity: "critical" | "warning" | "info";
}

export interface DecisionPipelineStep {
  id: string;
  label: string;
  completed: boolean;
  href: string;
  detail?: string;
}

export interface StoryTimelineStep {
  id: string;
  title: string;
  detail?: string;
  href?: string;
}

export interface ExecutiveBriefFact {
  id: string;
  label: string;
  value: string;
  hint?: string;
  tone?: "neutral" | "attention" | "positive" | "critical";
}

export interface ExecutiveBriefSection {
  id: string;
  label: string;
  body: string;
}

export interface ExecutiveCommandCenterModel {
  brief: string | null;
  briefParts: { domain: string; text: string }[];
  briefFacts: ExecutiveBriefFact[];
  briefSections: ExecutiveBriefSection[];
  healthScore: number;
  healthLevel: ExecutiveHealthLevel;
  healthLabelAr: string;
  indicators: ExecutiveIndicator[];
  alerts: ExecutiveAlert[];
  pipeline: DecisionPipelineStep[];
  storySteps: StoryTimelineStep[];
  departmentChart: { label: string; amount: number }[];
  boardRecommendation: string | null;
  narrativeStatus: string | null;
}
