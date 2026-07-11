"use client";

import * as React from "react";
import {
  ResponsiveContainer,
  type ResponsiveContainerProps,
} from "recharts";
import { cn } from "@/lib/utils";
import { colors } from "@/lib/tokens";

export const chartTheme = {
  primary: colors.goldPrimary,
  secondary: colors.goldLight,
  grid: "#E8E8E4",
  text: colors.grayMedium,
  surface: colors.white,
} as const;

export interface ChartContainerProps {
  children: React.ReactElement;
  height?: number;
  className?: string;
  responsiveProps?: Omit<ResponsiveContainerProps, "width" | "height" | "children">;
}

export function ChartContainer({
  children,
  height = 320,
  className,
  responsiveProps,
}: ChartContainerProps) {
  return (
    <div className={cn("w-full", className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%" {...responsiveProps}>
        {children}
      </ResponsiveContainer>
    </div>
  );
}
