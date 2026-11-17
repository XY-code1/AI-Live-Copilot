"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  FileText,
  Globe,
  Image as ImageIcon,
  PenLine,
  Upload,
} from "lucide-react";

import { ApiError, productApi, uploadProductSource } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Product } from "@/types";
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
import { EmptyState } from "@/components/common/empty-state";
import { PageHeader } from "@/components/common/page-header";
import { Input } from "@/components/ui/input";

type Mode = "pdf" | "url";

export default function ProductImportPage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [productId, setProductId] = useState("");
  const [mode, setMode] = useState<Mode>("pdf");
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [result, setResult] = useState<{ type: Mode; name: string } | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    productApi
      .list()
      .then((data) => {
        if (!active) return;
        setProducts(data);
        if (data.length > 0) setProductId((current) => current || data[0].id);
      })
      .catch((caught: unknown) => {
        if (!active) return;
        setLoadError(caught instanceof ApiError ? caught.message : "加载商品失败");
        setProducts([]);
      });
    return () => {
      active = false;
    };
  }, [reloadKey]);

  async function handleSubmit() {
    if (!productId) return;
    setSubmitting(true);
    setSubmitError(null);
    setResult(null);
    try {
      const source =
        mode === "pdf"
          ? await uploadProductSource(productId, file as File)
          : await productApi.createUrlSource(productId, url.trim());
      setResult({ type: mode, name: source.name });
      setFile(null);
      setUrl("");
    } catch (caught) {
      setSubmitError(caught instanceof ApiError ? caught.message : "导入失败");
    } finally {
      setSubmitting(false);
    }
  }

  const selectedProduct = products?.find((item) => item.id === productId);
  const canSubmit = Boolean(productId) && !submitting &&
    (mode === "pdf" ? Boolean(file) : url.trim().length > 0);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="商品导入"
        description="选择目标商品，上传 PDF/图片或导入商品链接，系统会保存来源并可供 AI 提取。"
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

      {products === null && !loadError ? <LoadingBlock rows={3} /> : null}

      {products !== null && products.length === 0 && !loadError ? (
        <EmptyState
          icon={Upload}
          title="还没有商品"
          description="先新建一个商品，再回来导入资料。"
          actionLabel="新建商品"
          onAction={() => router.push("/products/new")}
        />
      ) : null}

      {products !== null && products.length > 0 ? (
        <>
          <Card>
            <CardHeader>
              <CardTitle>选择目标商品</CardTitle>
              <CardDescription>资料会关联到这个商品，属性可追溯到来源。</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap items-center gap-3">
              <select
                value={productId}
                onChange={(event) => setProductId(event.target.value)}
                className="h-9 min-w-[16rem] rounded-md border border-input bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-label="目标商品"
              >
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name}
                  </option>
                ))}
              </select>
              <Link
                href="/products/new"
                className="text-sm text-primary hover:underline"
              >
                没有合适的？新建商品
              </Link>
              {selectedProduct ? (
                <Badge variant="secondary">{selectedProduct.category || "未分类"}</Badge>
              ) : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>导入方式</CardTitle>
              <CardDescription>支持 PDF、图片 OCR 和安全链接导入。</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => setMode("pdf")}
                  className={cn(
                    "flex items-center gap-2 rounded-md border px-3 py-2 text-sm font-medium transition-colors",
                    mode === "pdf"
                      ? "border-primary bg-accent text-accent-foreground"
                      : "border-border text-muted-foreground hover:bg-accent/50",
                  )}
                >
                  <FileText className="size-4" /> PDF / 图片
                </button>
                <button
                  type="button"
                  onClick={() => setMode("url")}
                  className={cn(
                    "flex items-center gap-2 rounded-md border px-3 py-2 text-sm font-medium transition-colors",
                    mode === "url"
                      ? "border-primary bg-accent text-accent-foreground"
                      : "border-border text-muted-foreground hover:bg-accent/50",
                  )}
                >
                  <Globe className="size-4" /> 商品链接
                </button>
              </div>

              {mode === "pdf" ? (
                <label
                  className="flex cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border px-6 py-10 text-center transition-colors hover:border-primary/50 hover:bg-accent/30"
                >
                  <Upload className="size-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">
                      {file ? file.name : "点击选择 PDF 或图片"}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      文件将保存到本地存储，并提取文本用于 AI 解析
                    </p>
                  </div>
                  <input
                    type="file"
                    accept="application/pdf,image/png,image/jpeg,image/webp,.pdf,.png,.jpg,.jpeg,.webp"
                    className="hidden"
                    onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                  />
                </label>
              ) : (
                <div className="flex flex-col gap-2">
                  <Input
                    value={url}
                    onChange={(event) => setUrl(event.target.value)}
                    placeholder="https:// 商品详情页链接"
                    aria-label="商品链接"
                  />
                  <p className="text-xs text-muted-foreground">
                    系统会抓取页面正文并保存，供 AI 提取使用。
                  </p>
                </div>
              )}

              {submitError ? (
                <p className="text-sm text-destructive" role="alert">
                  {submitError}
                </p>
              ) : null}

              <div className="flex gap-2">
                <Button onClick={handleSubmit} disabled={!canSubmit}>
                  {submitting ? "导入中…" : "开始导入"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {result ? (
            <Card>
              <CardContent className="flex flex-wrap items-center justify-between gap-3 p-5">
                <div className="flex items-center gap-3">
                  {result.type === "pdf" ? (
                    <FileText className="size-4 text-primary" />
                  ) : (
                    <Globe className="size-4 text-primary" />
                  )}
                  <div>
                    <p className="text-sm font-medium">导入成功：{result.name}</p>
                    <p className="text-xs text-muted-foreground">
                      已保存到「{selectedProduct?.name}」的资料来源，可在详情页查看文本或 AI 提取。
                    </p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push(`/products/${productId}`)}
                >
                  查看商品详情
                </Button>
              </CardContent>
            </Card>
          ) : null}

          <div className="grid gap-4 sm:grid-cols-2">
            <Card className="opacity-70">
              <CardContent className="flex items-start gap-4 p-5">
                <div className="flex size-10 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
                  <ImageIcon className="size-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold">图片 / 截图</h3>
                    <Badge variant="muted">后续支持</Badge>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">
                    已启用 PaddleOCR 中文识别，识别文本会作为可追溯商品资料保存。
                  </p>
                </div>
              </CardContent>
            </Card>
            <Card className="opacity-70">
              <CardContent className="flex items-start gap-4 p-5">
                <div className="flex size-10 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
                  <PenLine className="size-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold">手动录入</h3>
                    <Badge variant="muted">去新建</Badge>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">
                    直接填写商品信息，请在新建商品页完成。
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      ) : null}
    </div>
  );
}
