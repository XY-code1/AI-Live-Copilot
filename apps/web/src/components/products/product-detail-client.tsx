"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  FileText,
  Image as ImageIcon,
  Link2,
  Pencil,
  PenLine,
  Trash2,
} from "lucide-react";

import { ApiError, productApi } from "@/lib/api";
import type { ConfirmationStatus, Product, ProductSourceType } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ErrorBlock, LoadingBlock } from "@/components/common/state-blocks";
import { PageHeader } from "@/components/common/page-header";
import { formatDate, formatPrice } from "@/lib/format";

const confirmationMeta: Record<ConfirmationStatus, { label: string; variant: "success" | "warning" | "muted" }> = {
  confirmed: { label: "已确认", variant: "success" },
  unconfirmed: { label: "待确认", variant: "muted" },
  doubtful: { label: "存疑", variant: "warning" },
};

const sourceLabel: Record<ProductSourceType, string> = {
  pdf: "PDF",
  image: "图片",
  url: "链接",
  manual: "手动",
};

const sourceIcon: Record<ProductSourceType, typeof FileText> = {
  pdf: FileText,
  image: ImageIcon,
  url: Link2,
  manual: PenLine,
};

export function ProductDetailClient({ productId }: { productId: string }) {
  const router = useRouter();
  const [product, setProduct] = useState<Product | null>(null);
  const [state, setState] = useState<"loading" | "error" | "notfound" | "ready">(
    "loading",
  );
  const [deleting, setDeleting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    productApi
      .get(productId)
      .then((loaded) => {
        if (!active) return;
        setProduct(loaded);
        setState("ready");
      })
      .catch((caught: unknown) => {
        if (!active) return;
        setState(
          caught instanceof ApiError && caught.status === 404 ? "notfound" : "error",
        );
      });
    return () => {
      active = false;
    };
  }, [productId, reloadKey]);

  function retry() {
    setState("loading");
    setReloadKey((current) => current + 1);
  }

  async function remove() {
    if (!product) return;
    if (!window.confirm(`确定删除「${product.name}」？此操作不可撤销。`)) return;
    setDeleting(true);
    setActionError(null);
    try {
      await productApi.remove(product.id);
      router.push("/products");
      router.refresh();
    } catch (caught) {
      setActionError(caught instanceof ApiError ? caught.message : "删除失败");
      setDeleting(false);
    }
  }

  if (state === "loading") {
    return (
      <div className="flex flex-col gap-4">
        <LoadingBlock rows={4} />
      </div>
    );
  }

  if (state === "notfound") {
    return (
      <div className="flex flex-col gap-4">
        <ErrorBlock
          title="商品不存在"
          description="该商品可能已被删除。"
          onRetry={() => router.push("/products")}
        />
      </div>
    );
  }

  if (state === "error" || !product) {
    return (
      <ErrorBlock
        title="加载失败"
        description="无法加载商品详情，请重试。"
        onRetry={retry}
      />
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={product.name}
        description={`${product.category || "未分类"} · 更新于 ${formatDate(product.updatedAt)}`}
        actions={
          <div className="flex items-center gap-2">
            {product.price ? (
              <span className="text-lg font-semibold text-primary">
                {formatPrice(product.price, product.currency)}
              </span>
            ) : null}
            <Link
              href="/products"
              className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="size-4" /> 返回
            </Link>
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push(`/products/${product.id}/edit`)}
            >
              <Pencil /> 编辑
            </Button>
            <Button variant="destructive" size="sm" onClick={remove} disabled={deleting}>
              <Trash2 /> {deleting ? "删除中…" : "删除"}
            </Button>
          </div>
        }
      />

      {actionError ? (
        <p className="text-sm text-destructive" role="alert">
          {actionError}
        </p>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>商品属性</CardTitle>
          <CardDescription>
            AI 提取结果需保留来源与确认状态，未确认项不得用于宣传。
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col divide-y divide-border">
          {product.attributes.length === 0 ? (
            <p className="py-3 text-sm text-muted-foreground">
              暂无结构化属性，导入资料后由 AI 提取。
            </p>
          ) : (
            product.attributes.map((attribute) => {
              const meta = confirmationMeta[attribute.status];
              return (
                <div
                  key={attribute.id}
                  className="flex items-center justify-between gap-4 py-3"
                >
                  <span className="text-sm text-muted-foreground">{attribute.label}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium">{attribute.value}</span>
                    <Badge variant={meta.variant}>{meta.label}</Badge>
                  </div>
                </div>
              );
            })
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>资料来源</CardTitle>
          <CardDescription>每个属性都可追溯到原始资料。</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          {product.sources.length === 0 ? (
            <p className="text-sm text-muted-foreground">暂无关联资料。</p>
          ) : (
            product.sources.map((source) => {
              const Icon = sourceIcon[source.type];
              return (
                <div key={source.id} className="flex items-center gap-3 text-sm">
                  <Badge variant="outline" className="inline-flex items-center gap-1">
                    <Icon className="size-3.5" />
                    {sourceLabel[source.type]}
                  </Badge>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{source.name}</p>
                    {source.reference ? (
                      <p className="text-xs text-muted-foreground">{source.reference}</p>
                    ) : null}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {formatDate(source.createdAt)}
                  </span>
                </div>
              );
            })
          )}
        </CardContent>
      </Card>
    </div>
  );
}
