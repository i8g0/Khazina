export const colors = {
  goldPrimary: "#B8892D",
  goldDark: "#9A7425",
  goldLight: "#D8B56A",
  blackPrimary: "#111111",
  grayDark: "#1B1B1B",
  grayMedium: "#444444",
  bgLight: "#FAFAF8",
  white: "#FFFFFF",
} as const;

export const typography = {
  display: "text-4xl font-semibold leading-tight tracking-tight",
  h1: "text-3xl font-semibold leading-tight",
  h2: "text-2xl font-semibold leading-snug",
  h3: "text-xl font-medium leading-snug",
  h4: "text-lg font-medium leading-normal",
  body: "text-base font-normal leading-relaxed",
  bodySmall: "text-sm font-normal leading-relaxed",
  caption: "text-xs font-normal leading-normal",
  label: "text-sm font-medium leading-none",
} as const;

export const spacing = {
  section: "space-y-8",
  stack: "space-y-4",
  inline: "gap-3",
  card: "p-6",
  page: "p-8",
} as const;

export const radius = {
  sm: "rounded-md",
  md: "rounded-lg",
  lg: "rounded-xl",
  xl: "rounded-2xl",
  full: "rounded-full",
} as const;

export const shadows = {
  soft: "shadow-[0_1px_3px_rgba(17,17,17,0.06),0_4px_12px_rgba(17,17,17,0.04)]",
  card: "shadow-[0_2px_8px_rgba(17,17,17,0.06),0_8px_24px_rgba(17,17,17,0.04)]",
  elevated: "shadow-[0_4px_16px_rgba(17,17,17,0.08),0_12px_32px_rgba(17,17,17,0.06)]",
} as const;
