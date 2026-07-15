import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
      <h1 className="text-2xl font-bold text-foreground">الصفحة غير موجودة</h1>
      <p className="text-sm text-muted">تعذّر العثور على الصفحة المطلوبة.</p>
      <Link
        href="/"
        className="rounded-full border border-gold-primary bg-gold-primary px-5 py-2 text-sm font-medium text-white"
      >
        العودة للرئيسية
      </Link>
    </main>
  );
}
