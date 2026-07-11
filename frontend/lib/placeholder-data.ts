export const organization = {
  name: "مجموعة النخبة القابضة",
  platformName: "خزينة",
  reportingPeriod: "الربع الثاني 2026",
  executiveTitle: "الرئيس التنفيذي للشؤون المالية",
} as const;

export interface DashboardKpi {
  label: string;
  value: string;
  departmentBadge: string;
  hint: string;
  trend?: string;
}

export const dashboardKpis: DashboardKpi[] = [
  {
    label: "إجمالي الهدر المالي المكتشف",
    value: "2.34M ر.س",
    departmentBadge: "المشتريات",
    hint: "الربع الثاني 2026",
    trend: "-8.4% تحسّن",
  },
  {
    label: "عدد المخاطر الحرجة",
    value: "3",
    departmentBadge: "العمليات",
    hint: "7 مخاطر نشطة",
    trend: "+1",
  },
  {
    label: "التوفير المتوقع",
    value: "1.875M ر.س",
    departmentBadge: "تقنية المعلومات",
    hint: "14 توصية نشطة",
    trend: "+12.1%",
  },
  {
    label: "آخر توصية من الذكاء الاصطناعي",
    value: "دمج عقود الموردين",
    departmentBadge: "الموارد البشرية",
    hint: "ثقة 92%",
  },
  {
    label: "حالة آخر تحليل",
    value: "مكتمل",
    departmentBadge: "الامتثال",
    hint: "Procurement_Q2.xlsx",
    trend: "2026-06-28",
  },
];

export const wasteByDepartment = [
  { department: "المشتريات", waste: 745_000 },
  { department: "العمليات", waste: 520_000 },
  { department: "الشؤون المالية", waste: 310_000 },
  { department: "تقنية المعلومات", waste: 185_000 },
  { department: "الموارد البشرية", waste: 95_000 },
];

export const wasteTrend = [
  { month: "يناير", waste: 380_000 },
  { month: "فبراير", waste: 410_000 },
  { month: "مارس", waste: 395_000 },
  { month: "أبريل", waste: 420_000 },
  { month: "مايو", waste: 390_000 },
  { month: "يونيو", waste: 345_000 },
];

export interface DashboardRecommendation {
  id: string;
  title: string;
  description: string;
  badge: string;
  confidence: string;
}

export const dashboardRecommendations: DashboardRecommendation[] = [
  {
    id: "rec-w01",
    title: "دمج عقود الموردين المتداخلة",
    description:
      "توحيد 3 عقود مع مؤسسة التقنية المتقدمة لتقليل التكلفة السنوية",
    badge: "عالية",
    confidence: "92%",
  },
  {
    id: "rec-w02",
    title: "مراجعة سياسة السفر",
    description: "تطبيق موافقة مسبقة للرحلات فوق 15,000 ر.س",
    badge: "متوسطة",
    confidence: "87%",
  },
  {
    id: "rec-w03",
    title: "إلغاء اشتراكات غير مستخدمة",
    description: "12 اشتراك برمجي بدون استخدام خلال 90 يوماً",
    badge: "عالية",
    confidence: "95%",
  },
];

export interface TimelineEvent {
  id: string;
  date: string;
  title: string;
  type: string;
}

export const timelineEvents: TimelineEvent[] = [
  {
    id: "evt-001",
    date: "2026-06-28",
    title: "اكتشاف تجاوز ميزانية المشتريات",
    type: "تنبيه",
  },
  {
    id: "evt-002",
    date: "2026-06-25",
    title: "تحليل مخاطر الموردين مكتمل",
    type: "تحليل",
  },
  {
    id: "evt-003",
    date: "2026-06-20",
    title: "مراجعة امتثال العمليات",
    type: "مراجعة",
  },
  {
    id: "evt-004",
    date: "2026-06-15",
    title: "تحديث نموذج تقييم المخاطر",
    type: "نظام",
  },
  {
    id: "evt-005",
    date: "2026-06-10",
    title: "تقرير المخاطر الربعي",
    type: "تقرير",
  },
];

export interface RecentAnalysis {
  id: string;
  title: string;
  type: string;
  sourceFile: string;
  date: string;
  status: string;
}

export const recentAnalyses: RecentAnalysis[] = [
  {
    id: "ana-001",
    title: "تحليل هدر المشتريات Q2",
    type: "هدر مالي",
    sourceFile: "Procurement_Q2.xlsx",
    date: "2026-06-28",
    status: "مكتمل",
  },
  {
    id: "ana-002",
    title: "تقييم مخاطر الموردين",
    type: "مخاطر",
    sourceFile: "Supplier_Contracts.xlsx",
    date: "2026-06-25",
    status: "مكتمل",
  },
  {
    id: "ana-003",
    title: "محاكاة تقليل الإنفاق",
    type: "محاكاة",
    sourceFile: "Budget_Q2_2026.xlsx",
    date: "2026-06-20",
    status: "مكتمل",
  },
  {
    id: "ana-004",
    title: "مراجعة تكاليف التشغيل",
    type: "تشغيلي",
    sourceFile: "Operating_Costs.xlsx",
    date: "2026-06-18",
    status: "مكتمل",
  },
  {
    id: "ana-005",
    title: "تحليل الرواتب",
    type: "موارد بشرية",
    sourceFile: "Payroll_2026.xlsx",
    date: "2026-06-15",
    status: "قيد المعالجة",
  },
];

export const dashboardNavItems = [
  { id: "dashboard", label: "لوحة التحكم" },
  { id: "waste", label: "كشف الهدر" },
  { id: "risk", label: "إدارة المخاطر" },
  { id: "simulation", label: "محاكاة الأعمال" },
  { id: "reports", label: "التقارير" },
  { id: "data", label: "إدارة البيانات" },
] as const;

// ---------------------------------------------------------------------------
// Financial Waste Detection
// ---------------------------------------------------------------------------

export interface WasteUploadFile {
  fileName: string;
  department: string;
  size: string;
  status: string;
}

export const wasteUploadFiles: WasteUploadFile[] = [
  {
    fileName: "Procurement_Q2.xlsx",
    department: "المشتريات",
    size: "2.4 MB",
    status: "جاهز للتحليل",
  },
  {
    fileName: "Operating_Costs.xlsx",
    department: "العمليات",
    size: "1.1 MB",
    status: "جاهز للتحليل",
  },
  {
    fileName: "Supplier_Contracts.xlsx",
    department: "المشتريات",
    size: "3.8 MB",
    status: "جاهز للتحليل",
  },
];

export interface WasteAnalysisRow {
  id: string;
  category: string;
  amount: number;
  percentage: string;
  department: string;
}

export const wasteAnalysisResults: WasteAnalysisRow[] = [
  {
    id: "wa-001",
    category: "تكرار طلبات الشراء",
    amount: 420_000,
    percentage: "17.9%",
    department: "المشتريات",
  },
  {
    id: "wa-002",
    category: "أسعار موردين مرتفعة",
    amount: 680_000,
    percentage: "29.1%",
    department: "المشتريات",
  },
  {
    id: "wa-003",
    category: "سفر غير ضروري",
    amount: 310_000,
    percentage: "13.2%",
    department: "الشؤون المالية",
  },
  {
    id: "wa-004",
    category: "اشتراكات غير مستخدمة",
    amount: 185_000,
    percentage: "7.9%",
    department: "تقنية المعلومات",
  },
  {
    id: "wa-005",
    category: "عقود متداخلة",
    amount: 745_000,
    percentage: "31.9%",
    department: "العمليات",
  },
];

export const wasteByCategory = wasteAnalysisResults.map((row) => ({
  category: row.category,
  waste: row.amount,
}));

export interface WasteSummaryKpi {
  label: string;
  value: string;
  hint: string;
}

export const wasteSummaryKpis: WasteSummaryKpi[] = [
  {
    label: "إجمالي الهدر المكتشف",
    value: "2.34M ر.س",
    hint: "-8.4% تحسّن · الربع الثاني 2026",
  },
  {
    label: "نسبة الهدر",
    value: "4.8%",
    hint: "من إجمالي الإنفاق المحلل",
  },
  {
    label: "أعلى فئة هدر",
    value: "عقود متداخلة",
    hint: "31.9% · العمليات",
  },
  {
    label: "التوفير المحتمل",
    value: "1.875M ر.س",
    hint: "4 فرص توفير نشطة",
  },
];

export interface WasteRecommendation {
  id: string;
  title: string;
  description: string;
  badge: string;
  confidence: string;
  savings: string;
  department: string;
}

export const wasteRecommendations: WasteRecommendation[] = [
  {
    id: "rec-w01",
    title: "دمج عقود الموردين المتداخلة",
    description:
      "توحيد 3 عقود مع مؤسسة التقنية المتقدمة لتقليل التكلفة السنوية",
    badge: "عالية",
    confidence: "92%",
    savings: "520,000",
    department: "المشتريات",
  },
  {
    id: "rec-w02",
    title: "مراجعة سياسة السفر",
    description: "تطبيق موافقة مسبقة للرحلات فوق 15,000 ر.س",
    badge: "متوسطة",
    confidence: "87%",
    savings: "180,000",
    department: "العمليات",
  },
  {
    id: "rec-w03",
    title: "إلغاء اشتراكات غير مستخدمة",
    description: "12 اشتراك برمجي بدون استخدام خلال 90 يوماً",
    badge: "عالية",
    confidence: "95%",
    savings: "95,000",
    department: "تقنية المعلومات",
  },
  {
    id: "rec-w04",
    title: "إعادة التفاوض مع شركة الخليج",
    description: "أسعار أعلى 18% من متوسط السوق",
    badge: "عالية",
    confidence: "89%",
    savings: "340,000",
    department: "المشتريات",
  },
];

export interface WasteVendorDetail {
  id: string;
  vendor: string;
  category: string;
  amount: number;
  deviation: string;
  status: string;
}

export const wasteVendorDetails: WasteVendorDetail[] = [
  {
    id: "wv-001",
    vendor: "شركة الخليج للتوريدات",
    category: "الموردون",
    amount: 680_000,
    deviation: "+18%",
    status: "يتطلب مراجعة",
  },
  {
    id: "wv-002",
    vendor: "مؤسسة التقنية المتقدمة",
    category: "تقنية",
    amount: 420_000,
    deviation: "+12%",
    status: "يتطلب مراجعة",
  },
  {
    id: "wv-003",
    vendor: "مجموعة السفر المؤسسي",
    category: "السفر",
    amount: 310_000,
    deviation: "+25%",
    status: "حرج",
  },
];

export const wasteDepartmentFilterOptions = [
  "الكل",
  "المشتريات",
  "العمليات",
  "الشؤون المالية",
  "تقنية المعلومات",
] as const;
