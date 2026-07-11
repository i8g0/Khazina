import { cn } from "@/lib/utils";

export interface ResponsiveContainerProps {
  children: React.ReactNode;
  className?: string;
  size?: "sm" | "md" | "lg" | "xl" | "full";
}

const sizeClasses = {
  sm: "max-w-3xl",
  md: "max-w-5xl",
  lg: "max-w-6xl",
  xl: "max-w-7xl",
  full: "max-w-full",
};

export function ResponsiveContainer({
  children,
  className,
  size = "xl",
}: ResponsiveContainerProps) {
  return (
    <div className={cn("mx-auto w-full", sizeClasses[size], className)}>
      {children}
    </div>
  );
}
