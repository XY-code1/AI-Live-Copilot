"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Sparkles } from "lucide-react";

import { ApiError, comparisonApi, productApi, scriptApi } from "@/lib/api";
import type { Comparison, Product, Script } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { EmptyState } from "@/components/common/empty-state";
import { ErrorBlock, LoadingBlock } from "@/components/common/state-blocks";
import { PageHeader } from "@/components/common/page-header";
import { Input } from "@/components/ui/input";

const selectClass =
  "h-9 rounded-md border border-input bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

export default function ScriptsPage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[] | null>(null);
  const [comparisons, setComparisons] = useState<Comparison[]>([]);
  const [scripts, setScripts] = useState<Script[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const [productId, setProductId] = useState("");
  const [comparisonId, setComparisonId] = useState("");
  const [scenario, setScenario] = useState("日常带货");
  const [audience, setAudience] = useState("");
  const [style, setStyle] = useState("亲切自然");
  const [generating, setGenerating] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([productApi.list(), comparisonApi.listAll(), scriptApi.list()])
      .then(([productList, comparisonList, scriptList]) => {
        if (!active) return;
        setProducts(productList);
        setComparisons(comparisonList);
        setScripts(scriptList);
        if (productList.length > 0) setProductId((current) => current || productList[0].id);
      })
      .catch((caught: unknown) => {
        if (!active) return;
        setLoadError(caught instanceof ApiError ? caught.message : "加载失败");
      });
    return () => {
      active = false;
    };
  }, [reloadKey]);

  const productComparisons = useMemo(
    () => comparisons.filter((comparison) => comparison.productId === productId),
    [comparisons, productId],
  );

  const latestBySeries = useMemo(() => {
    const grouped = new Map<string, Script>();
    for (const script of scripts ?? []) {
      const existing = grouped.get(script.seriesId);
      if (!existing || script.version > existing.version) {
        grouped.set(script.seriesId, script);
      }
    }
    return Array.from(grouped.values());
  }, [scripts]);

  const productName = (id: string) =>
    products?.find((product) => product.id === id)?.name ?? "商品";

  async function generate() {
    if (!productId) return;
    setGenerating(true);
    setActionError(null);
    try {
      const script = await scriptApi.generate(productId, {
        scenario,
        audience,
        style,
        comparison_id: comparisonId || undefined,
      });
      router.push(`/scripts/${script.id}`);
    } catch (caught) {
      setActionError(caught instanceof ApiError ? caught.message : "生成失败");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="话术工作台"
        description="基于商品资料与竞品差异，生成结构化直播话术，并支持版本管理。"
      />

      {loadError ? (
        <ErrorBlock
          title="加载失败"
          description={loadError}
          onRetry={() => {
            setLoadError(null);
            setReloadKey((current) => current + 1);
          }}
        />
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>生成话术</CardTitle>
          <CardDescription>选择商品与可选的竞品对比，设定场景、人群与风格。</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={productId}
              onChange={(event) => {
                setProductId(event.target.value);
                setComparisonId("");
              }}
              className={selectClass}
              aria-label="商品"
            >
              {(products ?? []).map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
            <select
              value={comparisonId}
              onChange={(event) => setComparisonId(event.target.value)}
              className={selectClass}
              aria-label="竞品对比"
            >
              <option value="">不关联竞品</option>
              {productComparisons.map((comparison) => (
                <option key={comparison.id} value={comparison.id}>
                  vs {comparison.competitor?.productName ?? "竞品"}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Input
              value={scenario}
              onChange={(event) => setScenario(event.target.value)}
              placeholder="直播场景"
              className="max-w-[10rem]"
              aria-label="直播场景"
            />
            <Input
              value={audience}
              onChange={(event) => setAudience(event.target.value)}
              placeholder="目标人群"
              className="max-w-[10rem]"
              aria-label="目标人群"
            />
            <Input
              value={style}
              onChange={(event) => setStyle(event.target.value)}
              placeholder="话术风格"
              className="max-w-[10rem]"
              aria-label="话术风格"
            />
            <Button onClick={generate} disabled={generating || !productId}>
              <Sparkles /> {generating ? "生成中…" : "生成话术"}
            </Button>
          </div>
          {actionError ? (
            <p className="text-sm text-destructive" role="alert">
              {actionError}
            </p>
          ) : null}
        </CardContent>
      </Card>

      {scripts === null && !loadError ? <LoadingBlock rows={3} /> : null}

      {scripts !== null && !loadError ? (
        latestBySeries.length === 0 ? (
          <EmptyState
            icon={Sparkles}
            title="还没有话术"
            description="选择商品后点击「生成话术」，系统会生成结构化话术。"
          />
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            {latestBySeries.map((script) => (
              <Link
                key={script.id}
                href={`/scripts/${script.id}`}
                className="group flex flex-col gap-3 rounded-lg border border-border bg-card p-4 transition-colors hover:border-primary/40 hover:bg-accent/30"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h3 className="truncate text-sm font-semibold">{script.title}</h3>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      {productName(script.productId)} · v{script.version}
                    </p>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Badge variant="secondary">{script.status}</Badge>
                    <Badge
                      variant={
                        script.verificationStatus === "issue"
                          ? "warning"
                          : script.verificationStatus === "pass"
                            ? "success"
                            : "muted"
                      }
                    >
                      {script.verificationStatus === "issue"
                        ? "核验有问题"
                        : script.verificationStatus === "pass"
                          ? "已核验"
                          : "未核验"}
                    </Badge>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  <Badge variant="outline">{script.scenario || "日常带货"}</Badge>
                  {script.audience ? (
                    <Badge variant="outline">{script.audience}</Badge>
                  ) : null}
                  <Badge variant="outline">{script.style || "亲切自然"}</Badge>
                </div>
                <p className="line-clamp-2 text-xs text-muted-foreground">
                  {script.sections.find((section) => section.kind === "opening")?.content ??
                    script.sections[0]?.content ??
                    "暂无内容"}
                </p>
              </Link>
            ))}
          </div>
        )
      ) : null}
    </div>
  );
}
