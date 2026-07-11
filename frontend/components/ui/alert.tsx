import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { AlertCircle, CheckCircle2, Info, TriangleAlert } from "lucide-react";
import { cn } from "@/lib/utils";

const alertVariants = cva(
  "relative flex gap-3 rounded-xl border p-4 text-sm shadow-soft",
  {
    variants: {
      variant: {
        default: "border-border bg-surface text-black-primary",
        info: "border-info/20 bg-info/5 text-black-primary",
        success: "border-success/20 bg-success/5 text-black-primary",
        warning: "border-warning/20 bg-warning/5 text-black-primary",
        destructive: "border-destructive/20 bg-destructive/5 text-black-primary",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

const iconMap = {
  default: Info,
  info: Info,
  success: CheckCircle2,
  warning: TriangleAlert,
  destructive: AlertCircle,
};

export interface AlertProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> {
  title?: string;
}

function Alert({ className, variant = "default", title, children, ...props }: AlertProps) {
  const Icon = iconMap[variant ?? "default"];

  return (
    <div
      role="alert"
      className={cn(alertVariants({ variant }), className)}
      {...props}
    >
      <Icon className="mt-0.5 h-4 w-4 shrink-0 text-current opacity-80" />
      <div className="flex flex-col gap-1">
        {title ? <p className="font-medium leading-none">{title}</p> : null}
        {children ? (
          <div className="text-muted-foreground leading-relaxed">{children}</div>
        ) : null}
      </div>
    </div>
  );
}

export { Alert, alertVariants };
