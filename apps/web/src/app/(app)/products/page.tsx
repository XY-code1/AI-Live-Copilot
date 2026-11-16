"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FileText, Image as ImageIcon, Link2, PenLine, Plus, Search } from "lucide-react";

import { ApiError, productApi } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { ConfirmationStatus, Product, ProductSourceType } from "@/types";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { EmptyState } from "@/components/common/empty-state";
import { ErrorBlock, LoadingBlock } from "@/components/common/state-blocks";
import { PageHeader } from "@/components/common/page-header";
import { Input } from "@/components/ui/input";
import { formatPrice } from "@/lib/format";

const confirmationMeta: Record<ConfirmationStatus, { label: string; variant: "success" | "warning" | "muted" }> = {
  confirmed: { label: "已确认", variant: "success" },
  unconfirmed: { label: "待确认", variant: "muted" },
  doubtful: { label: "存疑", variant: "warning" },
};

const sourceIcon: Record<ProductSourceType, typeof FileText> = {
  pdf: FileText,
  image: ImageIcon,
  url: Link2,
  manual: PenLine,
};

function ProductCard({ product }: { product: Product }) {
  return (
    <Link
      href={`/products/${product.id}`}
      className="flex flex-col gap-3 rounded-lg border border-border bg-card p-4 transition-colors hover:border-primary/40 hover:bg-accent/30"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold">{product.name}</h3>
          <p className="mt-0.5 text-xs text-muted-foreground">
            {product.category || "未分类"}
          </p>
        </div>
        {product.price ? (
          <span className="text-sm font-semibold text-primary">
            {formatPrice(product.price, product.currency)}
          </span>
        ) : null}
      </div>

      <p className="line-clamp-2 text-xs text-muted-foreground">
        {product.summary || "暂无简介"}
      </p>

      {product.attributes.length > 0 ? (
        <div className="flex flex-wrap gap-1.5">
          {product.attributes.slice(0, 4).map((attribute) => {
            const meta = confirmationMeta[attribute.status];
            return (
              <Badge key={attribute.id} variant={meta.variant} className="normal-case">
                {attribute.label}：{attribute.value}
              </Badge>
            );
          })}
        </div>
      ) : null}

      {product.sources.length > 0 ? (
        <div className="flex flex-wrap items-center gap-3 border-t border-border pt-3 text-xs text-muted-foreground">
          {product.sources.map((source) => {
            const Icon = sourceIcon[source.type];
            return (
              <span key={source.id} className="inline-flex items-center gap-1">
                <Icon className="size-3.5" />
                {source.name}
              </span>
            );
          })}
        </div>
      ) : null}
    </Link>
  );
}

export default function ProductsPage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    productApi
      .list()
      .then((data) => {
        if (active) setProducts(data);
      })
      .catch((caught: unknown) => {
        if (!active) return;
        setError(caught instanceof ApiError ? caught.message : "加载失败");
        setProducts([]);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [reloadKey]);

  function load() {
    setLoading(true);
    setError(null);
    setReloadKey((current) => current + 1);
  }

  const filtered = useMemo(() => {
    if (!products) return [];
    const keyword = query.trim().toLowerCase();
    if (!keyword) return products;
    return products.filter((product) =>
      [product.name, product.category, product.summary]
        .join(" ")
        .toLowerCase()
        .includes(keyword),
    );
  }, [products, query]);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="商品知识库"
        description="管理已导入商品及其结构化属性。"
        actions={
          <div className="flex gap-2">
            <Link href="/products/import" className={buttonVariants({ variant: "outline" })}>
              导入商品
            </Link>
            <Link href="/products/new" className={buttonVariants()}>
              <Plus /> 新建商品
            </Link>
          </div>
        }
      />

      <div className="relative w-full sm:max-w-sm">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="搜索商品名称、分类或简介"
          className="pl-9"
          aria-label="搜索商品"
        />
      </div>

      {loading ? <LoadingBlock rows={3} /> : null}

      {error ? <ErrorBlock title="加载失败" description={error} onRetry={load} /> : null}

      {!loading && !error && filtered.length === 0 ? (
        <EmptyState
          icon={Search}
          title={query ? "没有匹配的商品" : "还没有商品"}
          description={
            query
              ? "尝试更换关键词。"
              : "新建一个商品，或从 PDF 导入商品资料。"
          }
          actionLabel={query ? undefined : "新建商品"}
          onAction={query ? undefined : () => router.push("/products/new")}
        />
      ) : null}

      {!loading && !error && filtered.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      ) : null}

      <p className={cn("text-xs text-muted-foreground", loading && "invisible")}>
        数据来源：{error ? "加载失败" : "本地 API（/api/v1/products）"}
      </p>
    </div>
  );
}
