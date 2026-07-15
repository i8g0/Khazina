"use client";

export default function GlobalError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="ar" dir="rtl">
      <body className="font-sans antialiased">
        <main className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
          <h1 className="text-2xl font-bold">حدث خطأ غير متوقع</h1>
          <p className="text-sm text-gray-600">تعذّر تحميل التطبيق. يرجى المحاولة مرة أخرى.</p>
          <button
            type="button"
            onClick={() => reset()}
            className="rounded-full border border-gray-800 bg-gray-900 px-5 py-2 text-sm font-medium text-white"
          >
            إعادة المحاولة
          </button>
        </main>
      </body>
    </html>
  );
}
