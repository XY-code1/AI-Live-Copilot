import { PageHeader } from "@/components/common/page-header";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { comparisons, competitors, products } from "@/lib/mock-data";
import type { EvidenceType } from "@/types";

const evidenceMeta: Record<EvidenceType, { label: string; variant: "success" | "warning" | "muted" }> = {
  source: { label: "资料支持", variant: "success" },
  inferred: { label: "推断", variant: "warning" },
  speculative: { label: "推测", variant: "muted" },
};

export default function AnalysisPage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="竞品分析"
        description="对比自家商品与竞品，区分资料支持的优势与 AI 推测。"
      />

      {comparisons.map((comparison) => {
        const product = products.find((item) => item.id === comparison.productId);
        const competitor = competitors.find((item) => item.id === comparison.competitorId);
        return (
          <Card key={comparison.id}>
            <CardHeader>
              <CardTitle>{product?.name ?? comparison.productId}</CardTitle>
              <CardDescription>对比 {competitor?.productName ?? comparison.competitorId}</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="flex flex-col divide-y divide-border rounded-md border border-border">
                {comparison.differences.map((difference) => {
                  const meta = evidenceMeta[difference.evidenceType];
                  return (
                    <div key={difference.id} className="grid gap-1 p-3 sm:grid-cols-[1fr_2fr_2fr] sm:gap-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">{difference.field}</span>
                        <Badge variant={meta.variant}>{meta.label}</Badge>
                      </div>
                      <span className="text-sm text-muted-foreground">{difference.ours}</span>
                      <span className="text-sm text-muted-foreground">{difference.theirs}</span>
                    </div>
                  );
                })}
              </div>

              {comparison.missingInfo.length > 0 ? (
                <div className="flex flex-wrap items-center gap-2 text-sm">
                  <span className="text-muted-foreground">待核实信息：</span>
                  {comparison.missingInfo.map((item) => (
                    <Badge key={item} variant="warning">
                      {item}
                    </Badge>
                  ))}
                </div>
              ) : null}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
