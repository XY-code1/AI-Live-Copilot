import { PageHeader } from "@/components/common/page-header";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { formatDate } from "@/lib/format";
import { products, scripts } from "@/lib/mock-data";
import type { ScriptStatus } from "@/types";

const statusMeta: Record<ScriptStatus, { label: string; variant: "success" | "warning" | "muted" }> = {
  draft: { label: "草稿", variant: "muted" },
  verified: { label: "已核验", variant: "success" },
  issue: { label: "有待核实", variant: "warning" },
};

export default function ScriptsPage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="话术工作台"
        description="生成、编辑与管理直播话术版本。"
      />

      <div className="grid gap-4 lg:grid-cols-2">
        {scripts.map((script) => {
          const product = products.find((item) => item.id === script.productId);
          const status = statusMeta[script.status];
          return (
            <Card key={script.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <CardTitle>{script.title}</CardTitle>
                    <CardDescription>
                      {product?.name} · v{script.version} · {formatDate(script.updatedAt)}
                    </CardDescription>
                  </div>
                  <Badge variant={status.variant}>{status.label}</Badge>
                </div>
              </CardHeader>
              <CardContent className="flex flex-col gap-3">
                <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                  <Badge variant="outline">{script.scenario}</Badge>
                  <Badge variant="outline">{script.audience}</Badge>
                  <Badge variant="outline">{script.style}</Badge>
                </div>
                <Separator />
                <div className="flex flex-col gap-3">
                  {script.sections.map((section) => (
                    <div key={section.id}>
                      <p className="text-xs font-semibold text-muted-foreground">
                        {section.title}
                      </p>
                      <p className="mt-1 text-sm">{section.content}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
