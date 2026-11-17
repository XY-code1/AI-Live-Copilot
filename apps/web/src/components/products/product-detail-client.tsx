"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  ChevronDown,
  FileText,
  Globe,
  Image as ImageIcon,
  Link2,
  Pencil,
  PenLine,
  Plus,
  Sparkles,
  Trash2,
  Upload,
  X,
} from "lucide-react";

import { ApiError, getSourceText, productApi, sourceApi, uploadProductSource } from "@/lib/api";
import type {
  ConfirmationStatus,
  Product,
  ProductSource,
  ProductSourceType,
  SourceSegment,
  SourceText,
} from "@/types";
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
import { Input } from "@/components/ui/input";
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

type Preview = { loading: boolean; text?: string; error?: string };

export function ProductDetailClient({ productId }: { productId: string }) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [product, setProduct] = useState<Product | null>(null);
  const [state, setState] = useState<"loading" | "error" | "notfound" | "ready">(
    "loading",
  );
  const [reloadKey, setReloadKey] = useState(0);
  const [deleting, setDeleting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [extracting, setExtracting] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [url, setUrl] = useState("");
  const [urlLoading, setUrlLoading] = useState(false);
  const [attrLabel, setAttrLabel] = useState("");
  const [attrValue, setAttrValue] = useState("");
  const [attrLoading, setAttrLoading] = useState(false);
  const [previews, setPreviews] = useState<Record<string, Preview>>({});
  const [segments, setSegments] = useState<Record<string, SourceSegment[]>>({});

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

  async function handleUpload(list: FileList | null) {
    const file = list?.[0];
    if (!file) return;
    setUploading(true);
    setUploadError(null);
    try {
      await uploadProductSource(productId, file);
      setReloadKey((current) => current + 1);
    } catch (caught) {
      setUploadError(caught instanceof ApiError ? caught.message : "上传失败");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleAddUrl() {
    const target = url.trim();
    if (!target) return;
    setUrlLoading(true);
    setNotice(null);
    setUploadError(null);
    try {
      await productApi.createUrlSource(productId, target);
      setUrl("");
      setNotice("链接已导入，可点击 AI 提取。");
      setReloadKey((current) => current + 1);
    } catch (caught) {
      setUploadError(caught instanceof ApiError ? caught.message : "链接导入失败");
    } finally {
      setUrlLoading(false);
    }
  }

  async function handleAddAttribute() {
    const label = attrLabel.trim();
    if (!label) return;
    setAttrLoading(true);
    setNotice(null);
    setUploadError(null);
    try {
      await productApi.addAttribute(productId, { label, value: attrValue.trim() });
      setAttrLabel("");
      setAttrValue("");
      setNotice("已添加手动属性。");
      setReloadKey((current) => current + 1);
    } catch (caught) {
      setUploadError(caught instanceof ApiError ? caught.message : "添加属性失败");
    } finally {
      setAttrLoading(false);
    }
  }

  async function handleDeleteAttribute(attributeId: string) {
    try {
      await productApi.deleteAttribute(attributeId);
      setReloadKey((current) => current + 1);
    } catch (caught) {
      setUploadError(caught instanceof ApiError ? caught.message : "删除失败");
    }
  }

  async function handleExtract() {
    setExtracting(true);
    setNotice(null);
    setUploadError(null);
    try {
      const updated = await productApi.extract(productId);
      setProduct(updated);
      setNotice(`已提取 ${updated.attributes.length} 个属性，来源与确认状态见下方。`);
    } catch (caught) {
      setUploadError(caught instanceof ApiError ? caught.message : "AI 提取失败");
    } finally {
      setExtracting(false);
    }
  }

  async function toggleSegments(source: ProductSource) {
    if (segments[source.id]) {
      setSegments((current) => {
        const next = { ...current };
        delete next[source.id];
        return next;
      });
      return;
    }
    try {
      const list = await sourceApi.segments(source.id);
      setSegments((current) => ({ ...current, [source.id]: list }));
    } catch (caught) {
      setUploadError(caught instanceof ApiError ? caught.message : "读取分段失败");
    }
  }

  async function togglePreview(source: ProductSource) {
    if (previews[source.id]?.text) {
      setPreviews((current) => {
        const next = { ...current };
        delete next[source.id];
        return next;
      });
      return;
    }
    setPreviews((current) => ({
      ...current,
      [source.id]: { loading: true },
    }));
    try {
      const text: SourceText = await getSourceText(source.id);
      setPreviews((current) => ({
        ...current,
        [source.id]: { loading: false, text: text.text },
      }));
    } catch (caught) {
      setPreviews((current) => ({
        ...current,
        [source.id]: {
          loading: false,
          error: caught instanceof ApiError ? caught.message : "读取失败",
        },
      }));
    }
  }

  if (state === "loading") {
    return <LoadingBlock rows={4} />;
  }

  if (state === "notfound") {
    return (
      <ErrorBlock
        title="商品不存在"
        description="该商品可能已被删除。"
        onRetry={() => router.push("/products")}
      />
    );
  }

  if (state === "error" || !product) {
    return (
      <ErrorBlock title="加载失败" description="无法加载商品详情，请重试。" onRetry={retry} />
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
          <CardTitle>上传资料</CardTitle>
          <CardDescription>
            支持 PDF 和图片 OCR。上传后自动提取文本并保存，供后续 AI 结构化提取使用。
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf,image/png,image/jpeg,image/webp,.pdf,.png,.jpg,.jpeg,.webp"
              className="hidden"
              onChange={(event) => handleUpload(event.target.files)}
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              <Upload /> {uploading ? "上传中…" : "选择 PDF / 图片"}
            </Button>
            <span className="text-xs text-muted-foreground">
              文件将保存到本地存储，提取文本后可在下方查看。
            </span>
          </div>
          <div className="flex flex-col gap-2">
            <span className="text-xs font-medium text-muted-foreground">链接导入</span>
            <div className="flex flex-wrap items-center gap-2">
              <Input
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder="粘贴商品详情页链接"
                className="max-w-sm"
                aria-label="商品链接"
              />
              <Button
                size="sm"
                variant="outline"
                onClick={handleAddUrl}
                disabled={urlLoading || !url.trim()}
              >
                <Globe /> {urlLoading ? "导入中…" : "导入链接"}
              </Button>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Button
              size="sm"
              onClick={handleExtract}
              disabled={extracting || !product.sources.some((source) => source.page_count !== null)}
            >
              <Sparkles /> {extracting ? "AI 提取中…" : "AI 提取"}
            </Button>
            <span className="text-xs text-muted-foreground">
              基于已上传资料的文本，抽取结构化属性并保留来源。
            </span>
          </div>

          {uploadError ? (
            <p className="text-sm text-destructive" role="alert">
              {uploadError}
            </p>
          ) : null}
          {notice ? (
            <p className="text-sm text-success" role="status">
              {notice}
            </p>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>商品属性</CardTitle>
          <CardDescription>
            AI 提取结果需保留来源与确认状态，未确认项不得用于宣传。
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <span className="text-xs font-medium text-muted-foreground">手动添加属性</span>
            <div className="flex flex-wrap items-center gap-2">
              <Input
                value={attrLabel}
                onChange={(event) => setAttrLabel(event.target.value)}
                placeholder="字段名，如：购物安排"
                className="max-w-[12rem]"
                aria-label="属性名"
              />
              <Input
                value={attrValue}
                onChange={(event) => setAttrValue(event.target.value)}
                placeholder="值，如：无购物"
                className="max-w-[16rem]"
                aria-label="属性值"
              />
              <Button
                size="sm"
                variant="outline"
                onClick={handleAddAttribute}
                disabled={attrLoading || !attrLabel.trim()}
              >
                <Plus /> 添加
              </Button>
            </div>
          </div>

          <div className="flex flex-col divide-y divide-border border-t border-border">
            {product.attributes.length === 0 ? (
              <p className="py-3 text-sm text-muted-foreground">
                暂无结构化属性，导入资料后由 AI 提取，或手动添加。
              </p>
            ) : (
              product.attributes.map((attribute) => {
                const meta = confirmationMeta[attribute.status];
                return (
                  <div
                    key={attribute.id}
                    className="flex items-center justify-between gap-4 py-3"
                  >
                    <div className="min-w-0">
                      <span className="text-sm text-muted-foreground">{attribute.label}</span>
                      {attribute.sourceReference ? (
                        <p className="truncate text-xs text-muted-foreground">
                          {attribute.sourceReference}
                        </p>
                      ) : null}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{attribute.value}</span>
                      <Badge variant={meta.variant}>{meta.label}</Badge>
                      <Badge variant="outline">
                        {attribute.origin === "ai" ? "AI" : "手动"}
                      </Badge>
                      <button
                        type="button"
                        onClick={() => handleDeleteAttribute(attribute.id)}
                        aria-label="删除属性"
                        className="rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-destructive"
                      >
                        <X className="size-4" />
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
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
              const preview = previews[source.id];
              const hasText = source.page_count !== null || preview?.text;
              return (
                <div key={source.id} className="flex flex-col gap-2">
                  <div className="flex items-center gap-3 text-sm">
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
                    {source.page_count !== null ? (
                      <span className="text-xs text-muted-foreground">
                        {source.page_count} 页
                      </span>
                    ) : null}
                    {source.parser ? (
                      <span className="text-xs text-muted-foreground">
                        {source.parser}
                      </span>
                    ) : null}
                    {source.contentHash ? (
                      <span className="text-xs text-muted-foreground">
                        sha256:{source.contentHash.slice(0, 8)}
                      </span>
                    ) : null}
                    <span className="text-xs text-muted-foreground">
                      {formatDate(source.createdAt)}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleSegments(source)}
                    >
                      分段
                    </Button>
                    {hasText ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => togglePreview(source)}
                    >
                        查看文本
                        <ChevronDown
                          className={`size-4 transition-transform ${preview?.text ? "rotate-180" : ""}`}
                        />
                      </Button>
                    ) : null}
                  </div>
                  {preview?.loading ? (
                    <LoadingBlock rows={1} />
                  ) : null}
                  {preview?.error ? (
                    <p className="text-xs text-destructive">{preview.error}</p>
                  ) : null}
                  {preview?.text !== undefined ? (
                    <pre className="max-h-72 overflow-auto rounded-md border border-border bg-muted/50 p-3 text-xs leading-relaxed whitespace-pre-wrap">
                      {preview.text || "（未提取到文本）"}
                    </pre>
                  ) : null}
                  {segments[source.id] ? (
                    <div className="flex flex-col gap-1 rounded-md border border-border bg-muted/30 p-2">
                      {segments[source.id].map((segment) => (
                        <div key={segment.id} className="text-xs">
                          <span className="font-medium text-muted-foreground">
                            {segment.kind}
                            {segment.pageNo ? ` · 第 ${segment.pageNo} 页` : ""}
                          </span>
                          {segment.kind === "table" && segment.structured?.rows ? (
                            <span className="ml-2 text-muted-foreground">
                              表格 {String(segment.structured.rows.length)} 行
                            </span>
                          ) : (
                            <p className="mt-0.5 line-clamp-2 whitespace-pre-wrap">
                              {segment.content || "（无文本，可能需要 OCR）"}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              );
            })
          )}
        </CardContent>
      </Card>
    </div>
  );
}
