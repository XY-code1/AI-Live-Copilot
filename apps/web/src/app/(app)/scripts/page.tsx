"use client";

import { useState } from "react";
import { PageHeader } from "@/components/common/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { formatDate } from "@/lib/format";
import { products, scripts as initialScripts } from "@/lib/mock-data";
import type { Script, ScriptStatus } from "@/types";

const statusMeta: Record<ScriptStatus, { label: string; variant: "success" | "warning" | "muted" }> = {
  draft: { label: "草稿", variant: "muted" },
  verified: { label: "已核验", variant: "success" },
  issue: { label: "有待核实", variant: "warning" },
};

export default function ScriptsPage() {
  const [scripts, setScripts] = useState<Script[]>(initialScripts);
  const [savedId, setSavedId] = useState<string | null>(null);

  function updateSection(scriptId: string, sectionId: string, content: string) {
    setScripts((current) =>
      current.map((script) =>
        script.id !== scriptId
          ? script
          : {
              ...script,
              sections: script.sections.map((section) =>
                section.id === sectionId ? { ...section, content } : section,
              ),
            },
      ),
    );
  }

  function save(script: Script) {
    setSavedId(script.id);
    window.setTimeout(() => setSavedId(null), 2000);
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="话术工作台"
        description="生成、编辑与管理直播话术版本。P1 可编辑与保存（演示）。"
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
                  <div className="flex items-center gap-2">
                    <Badge variant={status.variant}>{status.label}</Badge>
                    <Button size="sm" variant="outline" onClick={() => save(script)}>
                      {savedId === script.id ? "已保存" : "保存"}
                    </Button>
                  </div>
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
                      <Textarea
                        className="mt-1 min-h-0 text-sm"
                        rows={2}
                        value={section.content}
                        onChange={(event) =>
                          updateSection(script.id, section.id, event.target.value)
                        }
                        aria-label={section.title}
                      />
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
