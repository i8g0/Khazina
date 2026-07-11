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

// ---------------------------------------------------------------------------
// Risk Management
// ---------------------------------------------------------------------------

export interface RiskSummaryKpi {
  label: string;
  value: string;
  hint: string;
}

export const riskSummaryKpis: RiskSummaryKpi[] = [
  {
    label: "إجمالي المخاطر",
    value: "7",
    hint: "مخاطر نشطة وقيد المعالجة",
  },
  {
    label: "المخاطر الحرجة",
    value: "3",
    hint: "أولوية عالية",
  },
  {
    label: "المخاطر المتوسطة",
    value: "2",
    hint: "تتطلب متابعة",
  },
  {
    label: "المخاطر المغلقة",
    value: "0",
    hint: "خلال الربع الحالي",
  },
];

export const riskBySeverity = [
  { level: "عالية", count: 3 },
  { level: "متوسطة", count: 2 },
  { level: "منخفضة", count: 2 },
];

export const riskByDepartment = [
  { department: "المشتريات", score: 69 },
  { department: "العمليات", score: 78 },
  { department: "الشؤون المالية", score: 62 },
  { department: "تقنية المعلومات", score: 42 },
];

export const riskChartByCategory = [
  { category: "مالي", score: 78 },
  { category: "تشغيلي", score: 65 },
  { category: "امتثال", score: 82 },
  { category: "استراتيجي", score: 55 },
  { category: "تقني", score: 42 },
];

export interface RiskItem {
  id: string;
  name: string;
  description: string;
  priority: string;
  score: number;
  department: string;
  status: string;
  owner: string;
  lastUpdated: string;
}

export const riskItems: RiskItem[] = [
  {
    id: "risk-001",
    name: "تجاوز الميزانية التشغيلية",
    description: "تجاوز 8% عن ميزانية Q2 في المشتريات",
    priority: "عالية",
    score: 87,
    department: "المشتريات",
    status: "نشط",
    owner: "مدير المشتريات",
    lastUpdated: "2026-06-28",
  },
  {
    id: "risk-002",
    name: "تركّز الموردين",
    description: "62% من الإنفاق مع 3 موردين فقط",
    priority: "عالية",
    score: 82,
    department: "المشتريات",
    status: "نشط",
    owner: "مدير المشتريات",
    lastUpdated: "2026-06-25",
  },
  {
    id: "risk-003",
    name: "تأخر تحصيل الذمم",
    description: "متوسط التحصيل 47 يوماً",
    priority: "متوسطة",
    score: 65,
    department: "الشؤون المالية",
    status: "نشط",
    owner: "مدير الشؤون المالية",
    lastUpdated: "2026-06-22",
  },
  {
    id: "risk-004",
    name: "فجوة الامتثال",
    description: "2 عملية بدون موافقة مطلوبة",
    priority: "عالية",
    score: 78,
    department: "العمليات",
    status: "قيد المعالجة",
    owner: "مدير العمليات",
    lastUpdated: "2026-06-20",
  },
  {
    id: "risk-005",
    name: "تقلب أسعار الصرف",
    description: "تأثير 3.2% على تكلفة الواردات",
    priority: "متوسطة",
    score: 58,
    department: "الشؤون المالية",
    status: "نشط",
    owner: "مدير الشؤون المالية",
    lastUpdated: "2026-06-18",
  },
  {
    id: "risk-006",
    name: "نقص البيانات",
    description: "15% من السجلات بدون تصنيف",
    priority: "منخفضة",
    score: 42,
    department: "تقنية المعلومات",
    status: "نشط",
    owner: "مدير تقنية المعلومات",
    lastUpdated: "2026-06-15",
  },
  {
    id: "risk-007",
    name: "تأخر تقارير الموردين",
    description: "4 موردين متأخرين عن الجدول",
    priority: "منخفضة",
    score: 38,
    department: "المشتريات",
    status: "نشط",
    owner: "مدير المشتريات",
    lastUpdated: "2026-06-12",
  },
];

export interface RiskMatrixItem {
  id: string;
  name: string;
  likelihood: "منخفض" | "متوسط" | "مرتفع";
  impact: "منخفض" | "متوسط" | "مرتفع";
  priority: string;
}

export const riskMatrixItems: RiskMatrixItem[] = [
  {
    id: "risk-001",
    name: "تجاوز الميزانية",
    likelihood: "مرتفع",
    impact: "مرتفع",
    priority: "عالية",
  },
  {
    id: "risk-002",
    name: "تركّز الموردين",
    likelihood: "مرتفع",
    impact: "متوسط",
    priority: "عالية",
  },
  {
    id: "risk-003",
    name: "تأخر التحصيل",
    likelihood: "متوسط",
    impact: "متوسط",
    priority: "متوسطة",
  },
  {
    id: "risk-004",
    name: "فجوة الامتثال",
    likelihood: "متوسط",
    impact: "مرتفع",
    priority: "عالية",
  },
  {
    id: "risk-005",
    name: "تقلب الصرف",
    likelihood: "منخفض",
    impact: "متوسط",
    priority: "متوسطة",
  },
  {
    id: "risk-006",
    name: "نقص البيانات",
    likelihood: "منخفض",
    impact: "منخفض",
    priority: "منخفضة",
  },
];

export interface RiskRecommendation {
  id: string;
  title: string;
  description: string;
  priority: string;
}

export const riskRecommendations: RiskRecommendation[] = [
  {
    id: "rec-r01",
    title: "تنويع قاعدة الموردين",
    description: "تقليل الاعتماد على 3 موردين رئيسيين إلى أقل من 40%",
    priority: "عالية",
  },
  {
    id: "rec-r02",
    title: "تفعيل تنبيهات الميزانية",
    description: "تنبيه تلقائي عند 90% من حد الميزانية",
    priority: "عالية",
  },
  {
    id: "rec-r03",
    title: "مراجعة سياسة التحصيل",
    description: "تقليل متوسط أيام التحصيل إلى 35 يوماً",
    priority: "متوسطة",
  },
];

export interface RiskMitigationPlan {
  id: string;
  title: string;
  description: string;
  relatedRisk: string;
  status: string;
  targetDate: string;
  owner: string;
}

export const riskMitigationPlans: RiskMitigationPlan[] = [
  {
    id: "mit-001",
    title: "خطة تقليل تركّز الموردين",
    description: "إعادة توزيع 20% من الإنفاق على موردين بديلين خلال Q3",
    relatedRisk: "تركّز الموردين",
    status: "قيد التنفيذ",
    targetDate: "2026-09-30",
    owner: "مدير المشتريات",
  },
  {
    id: "mit-002",
    title: "تفعيل ضوابط الامتثال",
    description: "تطبيق موافقات إلزامية على العمليات الحرجة",
    relatedRisk: "فجوة الامتثال",
    status: "قيد المراجعة",
    targetDate: "2026-08-15",
    owner: "مدير العمليات",
  },
  {
    id: "mit-003",
    title: "برنامج تحسين التحصيل",
    description: "تقليل متوسط أيام التحصيل من 47 إلى 35 يوماً",
    relatedRisk: "تأخر تحصيل الذمم",
    status: "مخطط",
    targetDate: "2026-10-31",
    owner: "مدير الشؤون المالية",
  },
  {
    id: "mit-004",
    title: "مراقبة حدود الميزانية",
    description: "تنبيهات تلقائية عند 90% من حد الميزانية التشغيلية",
    relatedRisk: "تجاوز الميزانية",
    status: "قيد التنفيذ",
    targetDate: "2026-07-31",
    owner: "مدير المشتريات",
  },
];

// ---------------------------------------------------------------------------
// Business Simulation
// ---------------------------------------------------------------------------

export interface SimulationScenario {
  id: string;
  name: string;
  description: string;
  status: string;
}

export const simulationScenarios: SimulationScenario[] = [
  {
    id: "sim-001",
    name: "تقليل الإنفاق 10%",
    description: "محاكاة خفض الإنفاق التشغيلي 10% عبر جميع الأقسام",
    status: "مكتمل",
  },
  {
    id: "sim-002",
    name: "دمج الموردين",
    description: "محاكاة دمج 5 موردين إلى 3",
    status: "مسودة",
  },
  {
    id: "sim-003",
    name: "توسع السوق الخليجي",
    description: "محاكاة زيادة 15% في الإيرادات مع تكلفة توسع",
    status: "مسودة",
  },
];

export interface SimulationForecast {
  scenarioId: string;
  baselineLabel: string;
  baselineValue: string;
  projectedLabel: string;
  projectedValue: string;
  deltaLabel: string;
  deltaValue: string;
  confidence: string;
}

export const simulationForecasts: SimulationForecast[] = [
  {
    scenarioId: "sim-001",
    baselineLabel: "الأساس",
    baselineValue: "48.75M ر.س",
    projectedLabel: "المتوقع",
    projectedValue: "43.88M ر.س",
    deltaLabel: "التغير",
    deltaValue: "-10.0%",
    confidence: "88%",
  },
  {
    scenarioId: "sim-002",
    baselineLabel: "الأساس",
    baselineValue: "12.40M ر.س",
    projectedLabel: "المتوقع",
    projectedValue: "10.54M ر.س",
    deltaLabel: "التغير",
    deltaValue: "-15.0%",
    confidence: "85%",
  },
  {
    scenarioId: "sim-003",
    baselineLabel: "الأساس",
    baselineValue: "62.00M ر.س",
    projectedLabel: "المتوقع",
    projectedValue: "68.20M ر.س",
    deltaLabel: "التغير",
    deltaValue: "+10.0%",
    confidence: "72%",
  },
];

export interface SimulationChartPoint {
  quarter: string;
  baseline: number;
  projected: number;
}

export const simulationChartSeries: Record<string, SimulationChartPoint[]> = {
  "sim-001": [
    { quarter: "Q3 2026", baseline: 16_250_000, projected: 14_625_000 },
    { quarter: "Q4 2026", baseline: 16_250_000, projected: 14_625_000 },
    { quarter: "Q1 2027", baseline: 16_250_000, projected: 14_625_000 },
  ],
  "sim-002": [
    { quarter: "Q3 2026", baseline: 4_133_333, projected: 3_513_333 },
    { quarter: "Q4 2026", baseline: 4_133_333, projected: 3_513_333 },
    { quarter: "Q1 2027", baseline: 4_133_333, projected: 3_513_333 },
  ],
  "sim-003": [
    { quarter: "Q3 2026", baseline: 20_666_667, projected: 22_733_333 },
    { quarter: "Q4 2026", baseline: 20_666_667, projected: 22_733_333 },
    { quarter: "Q1 2027", baseline: 20_666_667, projected: 22_733_333 },
  ],
};

export interface SimulationComparisonMetric {
  metric: string;
  current: string;
  simulated: string;
  change: string;
  direction: "up" | "down" | "neutral";
}

export const simulationComparisonMetrics: Record<string, SimulationComparisonMetric[]> = {
  "sim-001": [
    {
      metric: "إجمالي الإنفاق",
      current: "48.75M",
      simulated: "43.88M",
      change: "-10.0%",
      direction: "down",
    },
    {
      metric: "عدد الموردين",
      current: "47",
      simulated: "32",
      change: "-31.9%",
      direction: "down",
    },
    {
      metric: "متوسط تكلفة العقد",
      current: "265,000",
      simulated: "228,000",
      change: "-14.0%",
      direction: "down",
    },
  ],
  "sim-002": [
    {
      metric: "تكلفة الموردين",
      current: "12.40M",
      simulated: "10.54M",
      change: "-15.0%",
      direction: "down",
    },
    {
      metric: "عدد الموردين النشطين",
      current: "47",
      simulated: "32",
      change: "-31.9%",
      direction: "down",
    },
    {
      metric: "تكلفة إدارية للموردين",
      current: "890K",
      simulated: "620K",
      change: "-30.3%",
      direction: "down",
    },
  ],
  "sim-003": [
    {
      metric: "إجمالي الإيرادات",
      current: "62.00M",
      simulated: "68.20M",
      change: "+10.0%",
      direction: "up",
    },
    {
      metric: "تكلفة التوسع",
      current: "0",
      simulated: "12.00M",
      change: "+12.00M",
      direction: "up",
    },
    {
      metric: "هامش الربح التشغيلي",
      current: "18.2%",
      simulated: "16.8%",
      change: "-1.4%",
      direction: "down",
    },
  ],
};

export interface SimulationAssumption {
  label: string;
  value: string;
}

export const simulationAssumptions: Record<string, SimulationAssumption[]> = {
  "sim-001": [
    { label: "نسبة خفض الإنفاق", value: "10%" },
    { label: "نطاق التطبيق", value: "جميع الأقسام" },
    { label: "تأثير على الإيرادات", value: "بدون تغيير" },
    { label: "الأفق الزمني", value: "3 أرباع" },
  ],
  "sim-002": [
    { label: "عدد الموردين قبل الدمج", value: "5" },
    { label: "عدد الموردين بعد الدمج", value: "3" },
    { label: "توفير إداري متوقع", value: "8%" },
    { label: "مدة التنفيذ", value: "6 أشهر" },
  ],
  "sim-003": [
    { label: "نمو الإيرادات المتوقع", value: "15%" },
    { label: "تكلفة التوسع", value: "12M ر.س" },
    { label: "الأسواق المستهدفة", value: "الخليج" },
    { label: "فترة تحقيق العائد", value: "18 شهراً" },
  ],
};

export interface SimulationImpactItem {
  category: string;
  baseline: string;
  projected: string;
  change: string;
  direction: "up" | "down" | "neutral";
}

export const simulationImpactBreakdown: Record<string, SimulationImpactItem[]> = {
  "sim-001": [
    {
      category: "المشتريات",
      baseline: "18.2M",
      projected: "16.4M",
      change: "-9.9%",
      direction: "down",
    },
    {
      category: "العمليات",
      baseline: "14.6M",
      projected: "13.1M",
      change: "-10.3%",
      direction: "down",
    },
    {
      category: "الشؤون المالية",
      baseline: "9.8M",
      projected: "8.8M",
      change: "-10.2%",
      direction: "down",
    },
    {
      category: "تقنية المعلومات",
      baseline: "6.15M",
      projected: "5.58M",
      change: "-9.3%",
      direction: "down",
    },
  ],
  "sim-002": [
    {
      category: "تكاليف العقود",
      baseline: "8.4M",
      projected: "7.1M",
      change: "-15.5%",
      direction: "down",
    },
    {
      category: "التكاليف الإدارية",
      baseline: "890K",
      projected: "620K",
      change: "-30.3%",
      direction: "down",
    },
    {
      category: "تكاليف الانتقال",
      baseline: "0",
      projected: "420K",
      change: "+420K",
      direction: "up",
    },
    {
      category: "التوفير الصافي",
      baseline: "12.4M",
      projected: "10.54M",
      change: "-15.0%",
      direction: "down",
    },
  ],
  "sim-003": [
    {
      category: "الإيرادات",
      baseline: "62.0M",
      projected: "68.2M",
      change: "+10.0%",
      direction: "up",
    },
    {
      category: "تكلفة التوسع",
      baseline: "0",
      projected: "12.0M",
      change: "+12.0M",
      direction: "up",
    },
    {
      category: "التكاليف التشغيلية",
      baseline: "50.7M",
      projected: "52.1M",
      change: "+2.8%",
      direction: "up",
    },
    {
      category: "صافي الأثر",
      baseline: "11.3M",
      projected: "4.1M",
      change: "-63.7%",
      direction: "down",
    },
  ],
};

export interface SimulationRecommendation {
  id: string;
  title: string;
  description: string;
  badge: string;
  confidence: string;
  department: string;
}

export const simulationRecommendations: SimulationRecommendation[] = [
  {
    id: "rec-s01",
    title: "البدء بخفض الإنفاق في المشتريات",
    description: "أعلى مساهمة في التوفير — 35% من إجمالي الأثر المتوقع",
    badge: "عالية",
    confidence: "88%",
    department: "المشتريات",
  },
  {
    id: "rec-s02",
    title: "مراجعة عقود الموردين قبل الدمج",
    description: "تحليل 5 عقود رئيسية لتحديد فرص التوفير الإضافية",
    badge: "عالية",
    confidence: "85%",
    department: "المشتريات",
  },
  {
    id: "rec-s03",
    title: "تقييم جدوى التوسع على مرحلتين",
    description: "تقليل مخاطر التوسع بتقسيم الاستثمار على 18 شهراً",
    badge: "متوسطة",
    confidence: "72%",
    department: "الشؤون المالية",
  },
];

export interface SimulationActionItem {
  id: string;
  title: string;
  description: string;
  status: string;
}

export const simulationActionItems: SimulationActionItem[] = [
  {
    id: "act-001",
    title: "اعتماد السيناريو للمراجعة التنفيذية",
    description: "إرسال نتائج المحاكاة إلى لجنة الشؤون المالية",
    status: "مقترح",
  },
  {
    id: "act-002",
    title: "تحديد خطة تنفيذ تدريجية",
    description: "تقسيم التغييرات على 3 أرباع لتقليل المخاطر التشغيلية",
    status: "مقترح",
  },
  {
    id: "act-003",
    title: "متابعة مؤشرات الأداء الرئيسية",
    description: "مراقبة الإنفاق والإيرادات شهرياً مقابل التوقعات",
    status: "مقترح",
  },
];

export interface SimulationResultSummary {
  title: string;
  description: string;
}

export const simulationResultSummaries: Record<string, SimulationResultSummary> = {
  "sim-001": {
    title: "توفير تشغيلي محتمل",
    description:
      "يشير السيناريو إلى توفير 4.87M ر.س خلال 3 أرباع مع ثقة 88%. يُنصح بالبدء بإدارة المشتريات.",
  },
  "sim-002": {
    title: "تخفيض تكاليف الموردين",
    description:
      "دمج الموردين قد يحقق توفيراً 1.86M ر.س سنوياً. يتطلب 6 أشهر للتنفيذ الكامل.",
  },
  "sim-003": {
    title: "نمو الإيرادات مع تكلفة توسع",
    description:
      "زيادة الإيرادات 10% مع استثمار توسع 12M ر.س. العائد المتوقع خلال 18 شهراً.",
  },
};

// ---------------------------------------------------------------------------
// Reports
// ---------------------------------------------------------------------------

export interface ReportSummaryKpi {
  label: string;
  value: string;
  hint: string;
}

export const reportSummaryKpis: ReportSummaryKpi[] = [
  {
    label: "إجمالي التقارير",
    value: "5",
    hint: "جميع التقارير المُنشأة",
  },
  {
    label: "تقارير جاهزة",
    value: "4",
    hint: "جاهزة للمعاينة والتصدير",
  },
  {
    label: "مسودات",
    value: "1",
    hint: "قيد الإعداد",
  },
  {
    label: "تقارير الربع الحالي",
    value: "5",
    hint: organization.reportingPeriod,
  },
];

export interface ReportItem {
  id: string;
  title: string;
  type: string;
  department: string;
  sourceFile: string;
  date: string;
  status: string;
  previewText: string;
}

export const reportItems: ReportItem[] = [
  {
    id: "rep-001",
    title: "تقرير الهدر المالي — Q2 2026",
    type: "تحليل",
    department: "الشؤون المالية",
    sourceFile: "Procurement_Q2.xlsx",
    date: "2026-06-30",
    status: "جاهز",
    previewText:
      "ملخص تنفيذي: يُظهر التقرير هدراً مالياً بقيمة 2.34M ر.س في الربع الثاني، مع تركّز 62% من الهدر في فئة الموردين.",
  },
  {
    id: "rep-002",
    title: "تقييم المخاطر الربعي",
    type: "مخاطر",
    department: "العمليات",
    sourceFile: "Operating_Costs.xlsx",
    date: "2026-06-25",
    status: "جاهز",
    previewText:
      "ملخص تنفيذي: 7 مخاطر نشطة — 3 حرجة. أعلى مخاطرة: تجاوز الميزانية التشغيلية في المشتريات.",
  },
  {
    id: "rep-003",
    title: "ملخص محاكاة تقليل الإنفاق",
    type: "محاكاة",
    department: "الشؤون المالية",
    sourceFile: "Budget_Q2_2026.xlsx",
    date: "2026-06-20",
    status: "جاهز",
    previewText:
      "ملخص تنفيذي: سيناريو خفض الإنفاق 10% يحقق توفيراً 4.87M ر.س خلال 3 أرباع بثقة 88%.",
  },
  {
    id: "rep-004",
    title: "تحليل الموردين",
    type: "مشتريات",
    department: "المشتريات",
    sourceFile: "Supplier_Contracts.xlsx",
    date: "2026-06-15",
    status: "مسودة",
    previewText:
      "مسودة: تحليل أولي لـ 47 مورداً — تركّز 62% من الإنفاق مع 3 موردين رئيسيين.",
  },
  {
    id: "rep-005",
    title: "تقرير الامتثال الشهري",
    type: "امتثال",
    department: "العمليات",
    sourceFile: "Payroll_2026.xlsx",
    date: "2026-06-01",
    status: "جاهز",
    previewText:
      "ملخص تنفيذي: نسبة الامتثال 96% — 2 عملية بدون موافقة مطلوبة تحتاج متابعة.",
  },
];

export const reportFilterOptions = {
  type: ["الكل", "تحليل", "مخاطر", "محاكاة", "مشتريات", "امتثال"],
  department: ["الكل", "الشؤون المالية", "المشتريات", "العمليات"],
  period: ["آخر 30 يوماً", "الربع الحالي", "2026"],
} as const;

export const reportExportFormats = [
  { id: "pdf", label: "تصدير PDF", icon: "pdf" },
  { id: "xlsx", label: "تصدير Excel", icon: "excel" },
  { id: "pptx", label: "تصدير PowerPoint", icon: "pptx" },
] as const;

// ---------------------------------------------------------------------------
// Data Management
// ---------------------------------------------------------------------------

export interface UploadedFileItem {
  id: string;
  fileName: string;
  department: string;
  uploadDate: string;
  size: string;
  status: string;
}

export const uploadedFiles: UploadedFileItem[] = [
  {
    id: "file-001",
    fileName: "Budget_Q2_2026.xlsx",
    department: "الشؤون المالية",
    uploadDate: "2026-06-18",
    size: "890 KB",
    status: "مكتمل",
  },
  {
    id: "file-002",
    fileName: "Supplier_Contracts.xlsx",
    department: "المشتريات",
    uploadDate: "2026-06-22",
    size: "3.8 MB",
    status: "قيد المعالجة",
  },
  {
    id: "file-003",
    fileName: "Procurement_Q2.xlsx",
    department: "المشتريات",
    uploadDate: "2026-06-28",
    size: "2.4 MB",
    status: "مكتمل",
  },
  {
    id: "file-004",
    fileName: "Payroll_2026.xlsx",
    department: "الموارد البشرية",
    uploadDate: "2026-06-15",
    size: "1.6 MB",
    status: "فشل",
  },
  {
    id: "file-005",
    fileName: "Operating_Costs.xlsx",
    department: "الشؤون المالية",
    uploadDate: "2026-06-25",
    size: "1.1 MB",
    status: "مكتمل",
  },
];

export interface ImportHistoryItem {
  date: string;
  file: string;
  records: string;
  status: string;
}

export const importHistory: ImportHistoryItem[] = [
  { date: "2026-06-28", file: "Procurement_Q2.xlsx", records: "4,820", status: "نجح" },
  { date: "2026-06-25", file: "Operating_Costs.xlsx", records: "1,240", status: "نجح" },
  { date: "2026-06-22", file: "Supplier_Contracts.xlsx", records: "—", status: "قيد المعالجة" },
  { date: "2026-06-18", file: "Budget_Q2_2026.xlsx", records: "2,150", status: "نجح" },
];

export interface DataValidationItem {
  check: string;
  result: string;
  details: string;
}

export const dataValidationSummary: DataValidationItem[] = [
  { check: "اكتمال الحقول", result: "94%", details: "312 سجل بدون تصنيف" },
  { check: "تطابق الميزانية", result: "98%", details: "2 تجاوزات" },
  { check: "تنسيق التاريخ", result: "100%", details: "—" },
  { check: "تكرار السجلات", result: "99.2%", details: "38 سجل مكرر" },
];

export interface DataSummaryKpi {
  label: string;
  value: string;
  hint: string;
}

export const dataSummaryKpis: DataSummaryKpi[] = [
  {
    label: "الملفات المرفوعة",
    value: "5",
    hint: "3 مكتملة · 1 قيد المعالجة",
  },
  {
    label: "إجمالي السجلات",
    value: "8,210",
    hint: "عبر جميع الملفات",
  },
  {
    label: "نسبة نجاح الاستيراد",
    value: "75%",
    hint: "3 من 4 عمليات ناجحة",
  },
  {
    label: "جودة البيانات",
    value: "97.8%",
    hint: "متوسط فحوصات التحقق",
  },
];

