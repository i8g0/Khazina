import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

export interface RecommendationCardProps {
  title: string;
  description: string;
  badge?: string;
  badgeVariant?: "default" | "secondary" | "success" | "warning" | "destructive" | "outline";
  footer?: React.ReactNode;
  className?: string;
}

export function RecommendationCard({
  title,
  description,
  badge,
  badgeVariant = "default",
  footer,
  className,
}: RecommendationCardProps) {
  return (
    <Card className={cn("transition-all hover:border-gold-primary/20", className)}>
      <CardContent className="space-y-4 p-6">
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-base font-semibold leading-snug text-black-primary">
            {title}
          </h3>
          {badge ? <Badge variant={badgeVariant}>{badge}</Badge> : null}
        </div>
        <p className="text-sm leading-relaxed text-muted">{description}</p>
        {footer ? <div className="pt-1">{footer}</div> : null}
      </CardContent>
    </Card>
  );
}
