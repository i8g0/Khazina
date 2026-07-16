import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { EXECUTIVE_LABELS } from "@/lib/executive-language";

export interface RecommendationCardProps {
  title: string;
  description: string;
  badge?: string;
  badgeVariant?: "default" | "secondary" | "success" | "warning" | "destructive" | "outline";
  footer?: React.ReactNode;
  problem?: string;
  evidence?: string;
  why?: string;
  rootCause?: string;
  businessImpact?: string;
  expectedSavings?: string;
  timeline?: string;
  ownerDepartment?: string;
  executiveAngle?: string;
  priorityRationale?: string;
  successKpi?: string;
  className?: string;
}

export function RecommendationCard({
  title,
  description,
  badge,
  badgeVariant = "default",
  footer,
  problem,
  evidence,
  why,
  rootCause,
  businessImpact,
  expectedSavings,
  timeline,
  ownerDepartment,
  executiveAngle,
  priorityRationale,
  successKpi,
  className,
}: RecommendationCardProps) {
  const hasStructured =
    Boolean(problem || evidence || businessImpact || expectedSavings || successKpi);

  return (
    <Card className={cn("transition-all hover:border-gold-primary/20", className)}>
      <CardContent className="space-y-4 p-6">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1">
            {problem ? (
              <p className="text-xs font-medium uppercase tracking-wide text-muted">
                {executiveAngle
                  ? `${executiveAngle} — ${EXECUTIVE_LABELS.businessProblem}`
                  : EXECUTIVE_LABELS.businessProblem}
              </p>
            ) : executiveAngle ? (
              <p className="text-xs font-medium uppercase tracking-wide text-muted">
                {executiveAngle}
              </p>
            ) : null}
            {problem ? (
              <p className="text-sm leading-relaxed text-muted">{problem}</p>
            ) : null}
            <h3 className="text-base font-semibold leading-snug text-black-primary">
              {title}
            </h3>
            <p className="text-xs text-muted">{EXECUTIVE_LABELS.decision}</p>
          </div>
          {badge ? (
            <Badge variant={badgeVariant}>
              {EXECUTIVE_LABELS.priority}: {badge}
            </Badge>
          ) : null}
        </div>

        {evidence ? (
          <p className="text-sm leading-relaxed text-muted">
            <span className="font-semibold text-gray-medium">
              {EXECUTIVE_LABELS.evidence}:{" "}
            </span>
            {evidence}
          </p>
        ) : null}

        {why || rootCause || priorityRationale ? (
          <p className="text-sm leading-relaxed text-muted">
            <span className="font-semibold text-gray-medium">
              {EXECUTIVE_LABELS.whyPriority}:{" "}
            </span>
            {priorityRationale || why || rootCause}
          </p>
        ) : null}

        {businessImpact ? (
          <p className="text-sm leading-relaxed text-muted">
            <span className="font-semibold text-gray-medium">
              {EXECUTIVE_LABELS.businessImpact}:{" "}
            </span>
            {businessImpact}
          </p>
        ) : null}

        {!hasStructured ? (
          <p className="text-sm leading-relaxed text-muted">{description}</p>
        ) : null}

        {expectedSavings || timeline || ownerDepartment || successKpi ? (
          <div className="grid gap-2 rounded-xl bg-muted/30 p-3 text-xs text-muted">
            {expectedSavings ? (
              <p>
                <span className="font-semibold">{EXECUTIVE_LABELS.expectedSavings}:</span>{" "}
                {expectedSavings}
              </p>
            ) : null}
            {successKpi ? (
              <p>
                <span className="font-semibold">{EXECUTIVE_LABELS.successKpi}:</span>{" "}
                {successKpi}
              </p>
            ) : null}
            {timeline ? (
              <p>
                <span className="font-semibold">{EXECUTIVE_LABELS.timeline}:</span>{" "}
                {timeline}
              </p>
            ) : null}
            {ownerDepartment ? (
              <p>
                <span className="font-semibold">{EXECUTIVE_LABELS.owner}:</span>{" "}
                {ownerDepartment}
              </p>
            ) : null}
          </div>
        ) : null}
        {footer ? <div className="pt-1">{footer}</div> : null}
      </CardContent>
    </Card>
  );
}
