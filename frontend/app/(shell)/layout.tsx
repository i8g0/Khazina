import { RootProviders } from "@/components/providers/root-providers";

export default function ShellLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <RootProviders>{children}</RootProviders>;
}
