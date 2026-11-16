"use client";

import { useEffect, useState } from "react";

import { ApiError, productApi } from "@/lib/api";
import type { Product } from "@/types";
import { ErrorBlock, LoadingBlock } from "@/components/common/state-blocks";
import { PageHeader } from "@/components/common/page-header";
import { ProductForm } from "@/components/products/product-form";

export function ProductEditClient({ productId }: { productId: string }) {
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    productApi
      .get(productId)
      .then((loaded) => {
        if (!active) return;
        setProduct(loaded);
      })
      .catch((caught: unknown) => {
        if (!active) return;
        setError(caught instanceof ApiError ? caught.message : "加载失败");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [productId]);

  if (loading) return <LoadingBlock rows={4} />;
  if (error || !product) {
    return <ErrorBlock title="加载失败" description={error ?? "商品不存在"} />;
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title={`编辑商品`} description={product.name} />
      <ProductForm product={product} submitLabel="保存修改" />
    </div>
  );
}
