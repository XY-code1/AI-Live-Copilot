"use client";

import { useEffect, useMemo, useState } from "react";
import { GitCompare, Plus, Users } from "lucide-react";

import { ApiError, competitorApi, comparisonApi, productApi } from "@/lib/api";
import type { Comparison, Competitor, Product } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ComparisonCard } from "@/components/analysis/comparison-card";
import { EmptyState } from "@/components/common/empty-state";
import { ErrorBlock, LoadingBlock } from "@/components/common/state-blocks";
import { PageHeader } from "@/components/common/page-header";
import { Input } from "@/components/ui/input";

const selectClass =
  "h-9 rounded-md border border-input bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

export default function AnalysisPage() {
  const [products, setProducts] = useState<Product[] | null>(null);
  const [competitors, setCompetitors] = useState<Competitor[] | null>(null);
  const [comparisons, setComparisons] = useState<Comparison[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [filter, setFilter] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  const [compName, setCompName] = useState("");
  const [compBrand, setCompBrand] = useState("");
  const [compPrice, setCompPrice] = useState("");
  const [compBusy, setCompBusy] = useState(false);

  const [newProductId, setNewProductId] = useState("");
  const [newCompetitorId, setNewCompetitorId] = useState("");
  const [createBusy, setCreateBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([productApi.list(), competitorApi.list(), comparisonApi.listAll()])
      .then(([productList, competitorList, comparisonList]) => {
        if (!active) return;
        setProducts(productList);
        setCompetitors(competitorList);
        setComparisons(comparisonList);
        if (productList.length > 0) setNewProductId((current) => current || productList[0].id);
        if (competitorList.length > 0) {
          setNewCompetitorId((current) => current || competitorList[0].id);
        }
      })
      .catch((caught: unknown) => {
        if (!active) return;
        setLoadError(caught instanceof ApiError ? caught.message : "加载失败");
      });
    return () => {
      active = false;
    };
  }, [reloadKey]);

  const productName = (id: string) =>
    products?.find((product) => product.id === id)?.name ?? "商品";

  const filtered = useMemo(() => {
    if (!comparisons) return [];
    if (!filter) return comparisons;
    return comparisons.filter((comparison) => comparison.productId === filter);
  }, [comparisons, filter]);

  function refresh() {
    setReloadKey((current) => current + 1);
  }

  async function addCompetitor() {
    if (!compName.trim()) return;
    setCompBusy(true);
    setActionError(null);
    try {
      await competitorApi.create({
        name: compName.trim(),
        brand: compBrand.trim(),
        price: compPrice.trim() ? Number(compPrice) : undefined,
      });
      setCompName("");
      setCompBrand("");
      setCompPrice("");
      refresh();
    } catch (caught) {
      setActionError(caught instanceof ApiError ? caught.message : "新建竞品失败");
    } finally {
      setCompBusy(false);
    }
  }

  async function addComparison() {
    if (!newProductId || !newCompetitorId) return;
    setCreateBusy(true);
    setActionError(null);
    try {
      await comparisonApi.create(newProductId, newCompetitorId);
      refresh();
    } catch (caught) {
      setActionError(caught instanceof ApiError ? caught.message : "创建对比失败");
    } finally {
      setCreateBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="竞品分析"
        description="对比自家商品与竞品，区分资料支持的优势与 AI 推测。"
      />

      {loadError ? (
        <ErrorBlock title="加载失败" description={loadError} onRetry={refresh} />
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>新建竞品</CardTitle>
            <CardDescription>录入竞品名称、品牌与价格。</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <Input
                value={compName}
                onChange={(event) => setCompName(event.target.value)}
                placeholder="竞品名称"
                className="max-w-[12rem]"
                aria-label="竞品名称"
              />
              <Input
                value={compBrand}
                onChange={(event) => setCompBrand(event.target.value)}
                placeholder="品牌"
                className="max-w-[9rem]"
                aria-label="品牌"
              />
              <Input
                value={compPrice}
                onChange={(event) => setCompPrice(event.target.value)}
                placeholder="价格"
                type="number"
                className="max-w-[7rem]"
                aria-label="价格"
              />
              <Button size="sm" onClick={addCompetitor} disabled={compBusy || !compName.trim()}>
                <Plus /> 添加竞品
              </Button>
            </div>
            {competitors && competitors.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {competitors.map((competitor) => (
                  <Badge key={competitor.id} variant="secondary">
                    {competitor.productName}
                  </Badge>
                ))}
              </div>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>新建对比</CardTitle>
            <CardDescription>选择一个自家商品和一个竞品。</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <select
                value={newProductId}
                onChange={(event) => setNewProductId(event.target.value)}
                className={selectClass}
                aria-label="自家商品"
              >
                {(products ?? []).map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name}
                  </option>
                ))}
              </select>
              <span className="text-sm text-muted-foreground">vs</span>
              <select
                value={newCompetitorId}
                onChange={(event) => setNewCompetitorId(event.target.value)}
                className={selectClass}
                aria-label="竞品"
              >
                {(competitors ?? []).map((competitor) => (
                  <option key={competitor.id} value={competitor.id}>
                    {competitor.productName}
                  </option>
                ))}
              </select>
              <Button
                size="sm"
                onClick={addComparison}
                disabled={createBusy || !newProductId || !newCompetitorId}
              >
                <Plus /> 创建对比
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              创建后可手动添加差异项；AI 自动生成差异将在后续支持。
            </p>
          </CardContent>
        </Card>
      </div>

      {actionError ? (
        <p className="text-sm text-destructive" role="alert">
          {actionError}
        </p>
      ) : null}

      {comparisons === null && !loadError ? <LoadingBlock rows={2} /> : null}

      {comparisons !== null && !loadError ? (
        <>
          <div className="flex flex-wrap items-center gap-3">
            <label className="text-sm text-muted-foreground" htmlFor="filter">
              按商品筛选
            </label>
            <select
              id="filter"
              value={filter}
              onChange={(event) => setFilter(event.target.value)}
              className={selectClass}
            >
              <option value="">全部商品</option>
              {(products ?? []).map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </div>

          {competitors?.length === 0 ? (
            <EmptyState
              icon={Users}
              title="先添加竞品"
              description="在上方新建竞品后，才能创建对比。"
            />
          ) : filtered.length === 0 ? (
            <EmptyState
              icon={GitCompare}
              title="还没有对比"
              description="在上方选择商品与竞品，创建你的第一条对比。"
              actionLabel="查看商品"
              onAction={() => undefined}
            />
          ) : (
            <div className="flex flex-col gap-4">
              {filtered.map((comparison) => (
                <ComparisonCard
                  key={comparison.id}
                  comparison={comparison}
                  productName={productName(comparison.productId)}
                  onChanged={refresh}
                />
              ))}
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}
