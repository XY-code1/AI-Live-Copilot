"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  FileText,
  FolderOpen,
  Image as ImageIcon,
  Library,
  Link2,
  PenLine,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { ApiError, productApi, scriptApi } from "@/lib/api";
import type { Product, ProductSourceType, Script } from "@/types";
import { Badge } from "@/components/ui/badge";
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
import { formatDate } from "@/lib/format";

type Filter = "all" | "product" | "script" | "source";

const sourceIcon: Record<ProductSourceType, LucideIcon> = {
  pdf: FileText,
  image: ImageIcon,
  url: Link2,
  manual: PenLine,
};

const sourceLabel: Record<ProductSourceType, string> = {
  pdf: "PDF",
  image: "图片",
  url: "链接",
  manual: "手动",
};

function verificationBadge(status?: string) {
  if (status === "issue") return <Badge variant="warning">核验有问题</Badge>;
  if (status === "pass") return <Badge variant="success">已核验</Badge>;
  return <Badge variant="muted">未核验</Badge>;
}

export default function AssetsPage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[] | null>(null);
  const [scripts, setScripts] = useState<Script[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("all");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    Promise.all([productApi.list(), scriptApi.list()])
      .then(([productList, scriptList]) => {
        if (!active) return;
        setProducts(productList);
        setScripts(scriptList);
      })
      .catch((caught: unknown) => {
        if (!active) return;
        setLoadError(caught instanceof ApiError ? caught.message : "加载失败");
      });
    return () => {
      active = false;
    };
  }, [reloadKey]);

  const latestScripts = useMemo(() => {
    const grouped = new Map<string, Script>();
    for (const script of scripts ?? []) {
      const existing = grouped.get(script.seriesId);
      if (!existing || script.version > existing.version) {
        grouped.set(script.seriesId, script);
      }
    }
    return Array.from(grouped.values());
  }, [scripts]);

  const sources = useMemo(() => {
    const rows: {
      id: string;
      name: string;
      type: ProductSourceType;
      pageCount: number | null;
      productName: string;
      productId: string;
    }[] = [];
    for (const product of products ?? []) {
      for (const source of product.sources) {
        rows.push({
          id: source.id,
          name: source.name,
          type: source.type,
          pageCount: source.page_count ?? null,
          productName: product.name,
          productId: product.id,
        });
      }
    }
    return rows;
  }, [products]);

  const issueCount = latestScripts.filter(
    (script) => script.verificationStatus === "issue",
  ).length;

  const stats = [
    { label: "商品", value: products?.length ?? 0, icon: Library },
    { label: "话术", value: latestScripts.length, icon: Sparkles },
    { label: "原始资料", value: sources.length, icon: FolderOpen },
    { label: "核验有问题", value: issueCount, icon: ShieldCheck },
  ];

  const productName = (id: string) =>
    products?.find((product) => product.id === id)?.name ?? "商品";

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="内容资产"
        description="商品、话术、原始资料与核验状态的统一视图。"
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

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardHeader className="flex flex-row items-center justify-between gap-2 p-4">
                <CardDescription>{stat.label}</CardDescription>
                <div className="flex size-8 items-center justify-center rounded-md bg-primary/10 text-primary">
                  <Icon className="size-4" />
                </div>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <p className="text-2xl font-semibold">{stat.value}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="flex flex-wrap gap-2">
        {(
          [
            ["all", "全部"],
            ["product", "商品"],
            ["script", "话术"],
            ["source", "原始资料"],
          ] as [Filter, string][]
        ).map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() => setFilter(value)}
            className={
              filter === value
                ? "rounded-md border border-primary bg-accent px-3 py-1.5 text-sm font-medium text-accent-foreground"
                : "rounded-md border border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent/50"
            }
          >
            {label}
          </button>
        ))}
      </div>

      {products === null || scripts === null ? (
        <LoadingBlock rows={3} />
      ) : (
        <>
          {(filter === "all" || filter === "product") &&
          (products?.length ?? 0) > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>商品</CardTitle>
                <CardDescription>已导入商品及其资料数量。</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col divide-y divide-border">
                {products.map((product) => (
                  <Link
                    key={product.id}
                    href={`/products/${product.id}`}
                    className="flex items-center justify-between gap-4 py-3 hover:bg-accent/30"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{product.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {product.category || "未分类"} · 属性 {product.attributes.length} · 资料{" "}
                        {product.sources.length}
                      </p>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(product.updatedAt)}
                    </span>
                  </Link>
                ))}
              </CardContent>
            </Card>
          ) : null}

          {(filter === "all" || filter === "script") &&
          latestScripts.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>话术</CardTitle>
                <CardDescription>按系列显示最新版本的核验状态。</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col divide-y divide-border">
                {latestScripts.map((script) => (
                  <Link
                    key={script.id}
                    href={`/scripts/${script.id}`}
                    className="flex items-center justify-between gap-4 py-3 hover:bg-accent/30"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{script.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {productName(script.productId)} · v{script.version} ·{" "}
                        {script.sections.length} 段
                      </p>
                    </div>
                    {verificationBadge(script.verificationStatus)}
                  </Link>
                ))}
              </CardContent>
            </Card>
          ) : null}

          {(filter === "all" || filter === "source") && sources.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>原始资料</CardTitle>
                <CardDescription>PDF、链接与图片等来源。</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col divide-y divide-border">
                {sources.map((source) => {
                  const Icon = sourceIcon[source.type];
                  return (
                    <Link
                      key={source.id}
                      href={`/products/${source.productId}`}
                      className="flex items-center justify-between gap-4 py-3 hover:bg-accent/30"
                    >
                      <div className="flex min-w-0 items-center gap-3">
                        <Icon className="size-4 shrink-0 text-muted-foreground" />
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium">{source.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {source.productName}
                          </p>
                        </div>
                      </div>
                      <div className="flex shrink-0 items-center gap-2">
                        <Badge variant="outline">{sourceLabel[source.type]}</Badge>
                        {source.pageCount !== null ? (
                          <span className="text-xs text-muted-foreground">
                            {source.pageCount} 页
                          </span>
                        ) : null}
                      </div>
                    </Link>
                  );
                })}
              </CardContent>
            </Card>
          ) : null}

          {(products?.length ?? 0) === 0 &&
          latestScripts.length === 0 &&
          sources.length === 0 &&
          !loadError ? (
            <EmptyState
              icon={FolderOpen}
              title="还没有内容资产"
              description="导入商品或生成话术后，会在这里统一汇总。"
              actionLabel="去导入商品"
              onAction={() => router.push("/products/import")}
            />
          ) : null}
        </>
      )}
    </div>
  );
}
