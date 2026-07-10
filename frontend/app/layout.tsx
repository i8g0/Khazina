import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Khazina",
  description: "Enterprise Financial Decision Intelligence Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <body className="antialiased">{children}</body>
    </html>
  );
}