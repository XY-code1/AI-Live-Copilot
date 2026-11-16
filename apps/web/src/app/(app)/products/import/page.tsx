"use client";

import { useRef, useState } from "react";
import { CloudUpload, FileText, Image as ImageIcon, Link2, PenLine } from "lucide-react";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ErrorBlock } from "@/components/common/state-blocks";
import { PageHeader } from "@/components/common/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import { products } from "@/lib/mock-data";
import type { ConfirmationStatus } from "@/types";

type ParseState = "idle" | "parsing" | "done" | "error";

const channels = [
  { key: "pdf", label: "PDF / 文档", description: "行程单、产品手册、合同", icon: FileText, enabled: true },
  { key: "image", label: "图片 / 截图", description: "OCR 识别与多模态理解（P2 后期）", icon: ImageIcon, enabled: false },
  { key: "url", label: "商品链接", description: "自动抓取详情页信息（P2）", icon: Link2, enabled: false },
  { key: "manual", label: "手动录入", description: "直接填写商品基础信息（P2）", icon: PenLine, enabled: false },
] as const;

const confirmationMeta: Record<ConfirmationStatus, { label: string; variant: "success" | "warning" | "muted" }> = {
  confirmed: { label: "已确认", variant: "success" },
  unconfirmed: { label: "待确认", variant: "muted" },
  doubtful: { label: "存疑", variant: "warning" },
};

const parsingSteps = ["读取文件", "提取文本", "结构化抽取", "关联来源"];

export default function ProductImportPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<ParseState>("idle");
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState<{ name: string; size: number } | null>(null);
  const [step, setStep] = useState(0);
  const [simulateFailure, setSimulateFailure] = useState(false);

  const demoAttributes = products[0]?.attributes ?? [];
  const pending = demoAttributes.filter((attribute) => attribute.status !== "confirmed").length;

  function startParsing(selected: { name: string; size: number }) {
    setFile(selected);
    setState("parsing");
    setStep(0);
    let current = 0;
    const timer = window.setInterval(() => {
      current += 1;
      if (current >= parsingSteps.length) {
        window.clearInterval(timer);
        setState(simulateFailure ? "error" : "done");
        return;
      }
      setStep(current);
    }, 600);
  }

  function handleFiles(list: FileList | null) {
    const picked = list?.[0];
    if (!picked) return;
    startParsing({ name: picked.name, size: picked.size });
  }

  function reset() {
    setState("idle");
    setFile(null);
    setStep(0);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="商品导入"
        description="选择一种方式导入商品资料，AI 将自动提取结构化信息。"
      />

      <div className="grid gap-4 sm:grid-cols-2">
        {channels.map((channel) => {
          const Icon = channel.icon;
          return (
            <Card key={channel.key} className={cn(!channel.enabled && "opacity-70")}>
              <CardContent className="flex items-start gap-4 p-5">
                <div className="flex size-10 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                  <Icon className="size-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold">{channel.label}</h3>
                    {channel.enabled ? (
                      <Badge variant="secondary">可用</Badge>
                    ) : (
                      <Badge variant="muted">P2</Badge>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">{channel.description}</p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardContent className="flex flex-col gap-4 p-5">
          <div
            role="button"
            tabIndex={0}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") inputRef.current?.click();
            }}
            onDragOver={(event) => {
              event.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(event) => {
              event.preventDefault();
              setDragging(false);
              handleFiles(event.dataTransfer.files);
            }}
            className={cn(
              "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border px-6 py-12 text-center transition-colors",
              dragging && "border-primary/60 bg-accent/40",
            )}
          >
            <div className="flex size-11 items-center justify-center rounded-full bg-primary/10 text-primary">
              <CloudUpload className="size-5" />
            </div>
            <div>
              <p className="text-sm font-medium">拖拽 PDF 到这里，或点击选择文件</p>
              <p className="mt-1 text-xs text-muted-foreground">
                演示模式：仅解析文件名与大小，不实际上传
              </p>
            </div>
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf,.pdf"
              className="hidden"
              onChange={(event) => handleFiles(event.target.files)}
            />
          </div>

          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <input
              type="checkbox"
              checked={simulateFailure}
              onChange={(event) => setSimulateFailure(event.target.checked)}
            />
            模拟解析失败（用于查看错误态）
          </label>
        </CardContent>
      </Card>

      {state === "parsing" && file ? (
        <Card>
          <CardContent className="flex flex-col gap-4 p-5" aria-busy="true">
            <div className="flex items-center gap-3">
              <FileText className="size-4 text-muted-foreground" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {Math.max(1, Math.round(file.size / 1024))} KB · 正在处理
                </p>
              </div>
            </div>
            <div className="flex flex-col gap-2">
              {parsingSteps.map((label, index) => (
                <div key={label} className="flex items-center gap-2 text-sm">
                  <span
                    className={cn(
                      "size-1.5 rounded-full",
                      index <= step ? "bg-primary" : "bg-muted",
                    )}
                  />
                  <span className={index <= step ? "text-foreground" : "text-muted-foreground"}>
                    {label}
                  </span>
                </div>
              ))}
            </div>
            <Skeleton className="h-16 w-full" />
          </CardContent>
        </Card>
      ) : null}

      {state === "done" && file ? (
        <Card>
          <CardContent className="flex flex-col gap-4 p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-sm font-semibold">解析完成</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  提取 {demoAttributes.length} 个属性，其中 {pending} 项待确认
                </p>
              </div>
              <Badge variant={pending > 0 ? "warning" : "success"}>
                {pending > 0 ? "有待确认" : "已确认"}
              </Badge>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {demoAttributes.map((attribute) => {
                const meta = confirmationMeta[attribute.status];
                return (
                  <Badge key={attribute.id} variant={meta.variant} className="normal-case">
                    {attribute.label}：{attribute.value}
                  </Badge>
                );
              })}
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={reset}>
                重新导入
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {state === "error" ? (
        <ErrorBlock
          title="解析失败"
          description="文件解析时出现问题，请重试或更换文件。"
          onRetry={() => {
            if (file) startParsing(file);
          }}
          className="flex-col items-start text-left"
        />
      ) : null}
    </div>
  );
}
