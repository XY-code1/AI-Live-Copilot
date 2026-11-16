"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Plus, Trash2, X } from "lucide-react";

import { ApiError, comparisonApi } from "@/lib/api";
import type { Comparison, EvidenceType, AdvantageSide } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const evidenceMeta: Record<EvidenceType, { label: string; variant: "success" | "warning" | "muted" }> = {
  source: { label: "资料支持", variant: "success" },
  inferred: { label: "推断", variant: "warning" },
  speculative: { label: "推测", variant: "muted" },
};

const sideMeta: Record<AdvantageSide, { label: string }> = {
  ours: { label: "我方优势" },
  theirs: { label: "对方优势" },
  neutral: { label: "中性" },
};

const selectClass =
  "h-8 rounded-md border border-input bg-background px-2 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

export function ComparisonCard({
  comparison,
  productName,
  onChanged,
}: {
  comparison: Comparison;
  productName: string;
  onChanged: () => void;
}) {
  const router = useRouter();
  const [field, setField] = useState("");
  const [ours, setOurs] = useState("");
  const [theirs, setTheirs] = useState("");
  const [evidenceType, setEvidenceType] = useState<EvidenceType>("source");
  const [side, setSide] = useState<AdvantageSide>("neutral");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function addDifference() {
    if (!field.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await comparisonApi.addDifference(comparison.id, {
        field: field.trim(),
        ours: ours.trim(),
        theirs: theirs.trim(),
        evidence_type: evidenceType,
        side,
      });
      setField("");
      setOurs("");
      setTheirs("");
      setEvidenceType("source");
      setSide("neutral");
      onChanged();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "添加失败");
    } finally {
      setBusy(false);
    }
  }

  async function removeDifference(differenceId: string) {
    try {
      await comparisonApi.removeDifference(differenceId);
      onChanged();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "删除失败");
    }
  }

  async function removeComparison() {
    if (!window.confirm("确定删除这条对比？")) return;
    try {
      await comparisonApi.remove(comparison.id);
      router.refresh();
      onChanged();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "删除失败");
    }
  }

  const competitor = comparison.competitor;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle>
              {productName} <span className="text-muted-foreground">vs</span>{" "}
              {competitor?.productName ?? "竞品"}
            </CardTitle>
            <CardDescription>
              {competitor?.brand || "—"} · 状态 {comparison.status}
            </CardDescription>
          </div>
          <Button variant="ghost" size="icon" onClick={removeComparison} aria-label="删除对比">
            <Trash2 className="size-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {comparison.missingInfo.length > 0 ? (
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="text-muted-foreground">待核实信息：</span>
            {comparison.missingInfo.map((item) => (
              <Badge key={item} variant="warning">
                {item}
              </Badge>
            ))}
          </div>
        ) : null}

        <div className="flex flex-col overflow-hidden rounded-md border border-border">
          <div className="grid grid-cols-[1fr_2fr_2fr] gap-4 border-b border-border bg-muted/40 p-3 text-xs font-medium text-muted-foreground">
            <span>字段</span>
            <span>我方</span>
            <span>对方</span>
          </div>
          {comparison.differences.length === 0 ? (
            <p className="p-3 text-sm text-muted-foreground">
              暂无差异项，可在下方手动添加，或由 AI 生成（后续）。
            </p>
          ) : (
            comparison.differences.map((difference) => {
              const meta = evidenceMeta[difference.evidenceType] ?? evidenceMeta.source;
              return (
                <div
                  key={difference.id}
                  className="grid grid-cols-[1fr_2fr_2fr] items-center gap-4 p-3"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-medium">{difference.field}</span>
                    <Badge variant={meta.variant}>{meta.label}</Badge>
                    <Badge variant="outline">{sideMeta[difference.side]?.label}</Badge>
                    <button
                      type="button"
                      onClick={() => removeDifference(difference.id)}
                      aria-label="删除差异"
                      className="rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-destructive"
                    >
                      <X className="size-3.5" />
                    </button>
                  </div>
                  <span className="text-sm text-muted-foreground">{difference.ours || "—"}</span>
                  <span className="text-sm text-muted-foreground">{difference.theirs || "—"}</span>
                </div>
              );
            })
          )}
        </div>

        <div className="flex flex-col gap-2">
          <span className="text-xs font-medium text-muted-foreground">添加差异项</span>
          <div className="flex flex-wrap items-center gap-2">
            <Input
              value={field}
              onChange={(event) => setField(event.target.value)}
              placeholder="字段"
              className="max-w-[9rem]"
              aria-label="字段"
            />
            <Input
              value={ours}
              onChange={(event) => setOurs(event.target.value)}
              placeholder="我方"
              className="max-w-[11rem]"
              aria-label="我方"
            />
            <Input
              value={theirs}
              onChange={(event) => setTheirs(event.target.value)}
              placeholder="对方"
              className="max-w-[11rem]"
              aria-label="对方"
            />
            <select
              value={evidenceType}
              onChange={(event) => setEvidenceType(event.target.value as EvidenceType)}
              className={selectClass}
              aria-label="证据类型"
            >
              <option value="source">资料支持</option>
              <option value="inferred">推断</option>
              <option value="speculative">推测</option>
            </select>
            <select
              value={side}
              onChange={(event) => setSide(event.target.value as AdvantageSide)}
              className={selectClass}
              aria-label="优势方"
            >
              <option value="neutral">中性</option>
              <option value="ours">我方优势</option>
              <option value="theirs">对方优势</option>
            </select>
            <Button size="sm" variant="outline" onClick={addDifference} disabled={busy || !field.trim()}>
              <Plus /> 添加
            </Button>
          </div>
          {error ? (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
