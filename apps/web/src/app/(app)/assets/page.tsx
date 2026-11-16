import { PageHeader } from "@/components/common/page-header";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatDate } from "@/lib/format";
import { assets } from "@/lib/mock-data";
import type { AssetKind } from "@/types";

const kindMeta: Record<AssetKind, { label: string; variant: "default" | "secondary" | "outline" }> = {
  analysis: { label: "分析", variant: "default" },
  script: { label: "话术", variant: "secondary" },
  source: { label: "资料", variant: "outline" },
};

export default function AssetsPage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="内容资产"
        description="历史分析、话术版本与原始资料。"
      />
      <Card>
        <CardHeader>
          <CardTitle>全部资产</CardTitle>
          <CardDescription>按类型查看与追溯。</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col divide-y divide-border">
          {assets.map((asset) => {
            const meta = kindMeta[asset.kind];
            return (
              <div key={asset.id} className="flex items-center justify-between gap-4 py-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{asset.name}</p>
                  <p className="text-xs text-muted-foreground">{asset.productName}</p>
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <Badge variant={meta.variant}>{meta.label}</Badge>
                  <span className="hidden text-xs text-muted-foreground sm:inline">
                    {formatDate(asset.updatedAt)}
                  </span>
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}
