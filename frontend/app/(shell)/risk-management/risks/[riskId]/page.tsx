import { RiskDetailPage } from "@/components/risk/risk-detail-page";

interface PageProps {
  params: Promise<{ riskId: string }>;
}

export default async function Page({ params }: PageProps) {
  const { riskId } = await params;
  return <RiskDetailPage riskId={riskId} />;
}
