import { notFound } from "next/navigation";
import { FileText, Image as ImageIcon, Link2, PenLine } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate, formatPrice } from "@/lib/format";
import { products } from "@/lib/mock-data";
import type { ConfirmationStatus, ProductSourceType } from "@/types";

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

export default async function ProductDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const product = products.find((item) => item.id === id);
  if (!product) notFound();

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={product.name}
        description={`${product.category} · 更新于 ${formatDate(product.updatedAt)}`}
        actions={
          product.price ? (
            <span className="text-lg font-semibold text-primary">
              {formatPrice(product.price, product.currency)}
            </span>
          ) : undefined
        }
      />

      <Card>
        <CardHeader>
          <CardTitle>商品属性</CardTitle>
          <CardDescription>
            AI 提取结果需保留来源与确认状态，未确认项不得用于宣传。
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col divide-y divide-border">
          {product.attributes.map((attribute) => {
            const meta = confirmationMeta[attribute.status];
            return (
              <div key={attribute.id} className="flex items-center justify-between gap-4 py-3">
                <span className="text-sm text-muted-foreground">{attribute.label}</span>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium">{attribute.value}</span>
                  <Badge variant={meta.variant}>{meta.label}</Badge>
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>资料来源</CardTitle>
          <CardDescription>每个属性都可追溯到原始资料。</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          {product.sources.map((source) => (
            <div key={source.id} className="flex items-center gap-3 text-sm">
              <Badge variant="outline" className="inline-flex items-center gap-1">
                {(() => {
                  const Icon = sourceIcon[source.type];
                  return <Icon className="size-3.5" />;
                })()}
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
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
