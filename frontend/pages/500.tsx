export default function ServerErrorExportPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "system-ui, sans-serif",
        textAlign: "center",
        padding: "2rem",
      }}
    >
      <h1 style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>
        حدث خطأ غير متوقع
      </h1>
      <p style={{ color: "#666" }}>تعذّر تحميل الصفحة. أعد المحاولة بعد قليل.</p>
    </main>
  );
}
