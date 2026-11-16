"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, productApi } from "@/lib/api";
import type { Product } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

type ProductFormProps = {
  product?: Product;
  submitLabel?: string;
};

export function ProductForm({ product, submitLabel }: ProductFormProps) {
  const router = useRouter();
  const [name, setName] = useState(product?.name ?? "");
  const [category, setCategory] = useState(product?.category ?? "");
  const [price, setPrice] = useState(product?.price?.toString() ?? "");
  const [summary, setSummary] = useState(product?.summary ?? "");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const payload = {
        name: name.trim(),
        category: category.trim(),
        summary: summary.trim(),
        price: price.trim() === "" ? undefined : Number(price),
      };
      const saved = product
        ? await productApi.update(product.id, payload)
        : await productApi.create(payload);
      router.push(`/products/${saved.id}`);
      router.refresh();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "保存失败，请重试");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card>
      <CardContent className="flex flex-col gap-4 p-5">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Label htmlFor="name">商品名称</Label>
            <Input
              id="name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
              placeholder="例如：川西五日游"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label htmlFor="category">分类</Label>
              <Input
                id="category"
                value={category}
                onChange={(event) => setCategory(event.target.value)}
                placeholder="例如：旅游线路"
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="price">价格（元）</Label>
              <Input
                id="price"
                type="number"
                min={0}
                step="0.01"
                value={price}
                onChange={(event) => setPrice(event.target.value)}
                placeholder="例如：3280"
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="summary">简介</Label>
            <Textarea
              id="summary"
              value={summary}
              onChange={(event) => setSummary(event.target.value)}
              placeholder="一句话描述商品卖点"
            />
          </div>

          {error ? (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}

          <div className="flex gap-2">
            <Button type="submit" disabled={submitting}>
              {submitting ? "保存中…" : submitLabel ?? "保存商品"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
              disabled={submitting}
            >
              取消
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
