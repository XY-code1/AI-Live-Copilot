"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  Check,
  Plus,
  Save,
  ShieldCheck,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";

import { ApiError, scriptApi, verificationApi } from "@/lib/api";
import type {
  IssueType,
  Script,
  ScriptSection,
  ScriptSectionKind,
  ScriptVerification,
} from "@/types";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ErrorBlock, LoadingBlock } from "@/components/common/state-blocks";
import { PageHeader } from "@/components/common/page-header";
import { Textarea } from "@/components/ui/textarea";

const KIND_LABEL: Record<ScriptSectionKind, string> = {
  opening: "开场吸引",
  intro: "商品介绍",
  selling_points: "核心卖点",
  differentiation: "差异化",
  interaction: "用户互动",
  closing: "促单引导",
  risk: "风险提示",
};

const selectClass =
  "h-8 rounded-md border border-input bg-background px-2 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

const ISSUE_TYPE_LABEL: Record<IssueType, string> = {
  unsupported_claim: "无资料支持",
  exaggeration: "夸大表述",
  absolute_wording: "绝对化表述",
  price_mismatch: "价格/费用不一致",
  missing_restriction: "遗漏限制条件",
  source_missing: "缺少来源",
};

export function ScriptEditor({ scriptId }: { scriptId: string }) {
  const router = useRouter();
  const [versions, setVersions] = useState<Script[]>([]);
  const [current, setCurrent] = useState<Script | null>(null);
  const [draft, setDraft] = useState<ScriptSection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [newKind, setNewKind] = useState<ScriptSectionKind>("selling_points");
  const [rewritingId, setRewritingId] = useState<string | null>(null);
  const [suggestion, setSuggestion] = useState<{
    sectionId: string;
    content: string;
  } | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [verification, setVerification] = useState<ScriptVerification | null>(null);

  useEffect(() => {
    let active = true;
    scriptApi
      .versions(scriptId)
      .then((list) => {
        if (!active) return;
        const sorted = [...list].sort((a, b) => b.version - a.version);
        setVersions(sorted);
        setCurrent(sorted[0] ?? null);
        setDraft(sorted[0]?.sections ?? []);
        setVerification(null);
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
  }, [scriptId]);

  const dirty =
    current !== null && JSON.stringify(draft) !== JSON.stringify(current.sections);

  function selectVersion(id: string) {
    if (dirty && !window.confirm("有未保存的修改，切换版本将丢失。继续？")) return;
    const found = versions.find((item) => item.id === id);
    if (!found) return;
    setCurrent(found);
    setDraft(found.sections);
    setSuggestion(null);
    setVerification(null);
  }

  function updateSection(id: string, patch: Partial<ScriptSection>) {
    setDraft((currentDraft) =>
      currentDraft.map((section) =>
        section.id === id ? { ...section, ...patch } : section,
      ),
    );
  }

  function removeSection(id: string) {
    setDraft((currentDraft) => currentDraft.filter((section) => section.id !== id));
    setSuggestion((current) =>
      current?.sectionId === id ? null : current,
    );
  }

  function addSection() {
    setDraft((currentDraft) => [
      ...currentDraft,
      {
        id: `draft-${crypto.randomUUID()}`,
        scriptId: current?.id ?? "",
        kind: newKind,
        title: KIND_LABEL[newKind],
        content: "",
        position: currentDraft.length,
        origin: "manual",
      },
    ]);
  }

  async function saveVersion() {
    if (!current) return;
    setSaving(true);
    setError(null);
    try {
      const saved = await scriptApi.saveVersion(current.id, {
        sections: draft.map((section) => ({
          kind: section.kind,
          title: section.title,
          content: section.content,
        })),
      });
      router.push(`/scripts/${saved.id}`);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "保存失败");
    } finally {
      setSaving(false);
    }
  }

  async function handleRewrite(section: ScriptSection) {
    if (!current) return;
    setRewritingId(section.id);
    setError(null);
    try {
      const result = await scriptApi.rewriteSection(current.id, section.id);
      setSuggestion({ sectionId: section.id, content: result.content });
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "AI 改写失败");
    } finally {
      setRewritingId(null);
    }
  }

  function acceptSuggestion() {
    if (!suggestion) return;
    updateSection(suggestion.sectionId, { content: suggestion.content });
    setSuggestion(null);
  }

  function exportMarkdown() {
    if (!current) return;
    const lines = [
      `# ${current.title}`,
      "",
      `> 商品：${current.productId} · 版本 v${current.version} · 场景：${current.scenario || "-"} · 人群：${current.audience || "-"} · 风格：${current.style || "-"}`,
      "",
    ];
    for (const section of draft) {
      lines.push(`## ${section.title || KIND_LABEL[section.kind]}`);
      lines.push("");
      lines.push(section.content);
      lines.push("");
    }
    const blob = new Blob([lines.join("\n")], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${current.title}-v${current.version}.md`;
    link.click();
    URL.revokeObjectURL(url);
  }

  async function handleVerify() {
    if (!current) return;
    setVerifying(true);
    setError(null);
    try {
      const report = await verificationApi.verify(current.id);
      setVerification(report);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "核验失败");
    } finally {
      setVerifying(false);
    }
  }

  async function removeScript() {
    if (!current || !window.confirm("确定删除该话术的所有版本？")) return;
    try {
      await scriptApi.remove(current.id);
      router.push("/scripts");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "删除失败");
    }
  }

  if (loading) return <LoadingBlock rows={4} />;

  if (!current) {
    return <ErrorBlock title="加载失败" description={error ?? "话术不存在"} />;
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={current.title}
        description={`${current.scenario || "日常带货"} · ${current.audience || "未设人群"} · ${current.style || "亲切自然"}`}
        actions={
          <div className="flex items-center gap-2">
            <Link
              href="/scripts"
              className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="size-4" /> 返回
            </Link>
            <Button
              variant="outline"
              size="sm"
              onClick={handleVerify}
              disabled={verifying}
            >
              <ShieldCheck /> {verifying ? "核验中…" : "事实核验"}
            </Button>
            <Button variant="outline" size="sm" onClick={exportMarkdown}>
              导出 Markdown
            </Button>
            <Button variant="destructive" size="sm" onClick={removeScript}>
              <Trash2 /> 删除
            </Button>
          </div>
        }
      />

      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-muted-foreground" htmlFor="version">
          版本
        </label>
        <select
          id="version"
          value={current.id}
          onChange={(event) => selectVersion(event.target.value)}
          className={selectClass}
        >
          {versions.map((version) => (
            <option key={version.id} value={version.id}>
              v{version.version}
            </option>
          ))}
        </select>
        <span className="text-xs text-muted-foreground">
          共 {versions.length} 个版本 · 编辑后保存将生成新版本
        </span>
      </div>

      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      {verification ? (
        <Card
          className={
            verification.status === "issue"
              ? "border-warning/50"
              : "border-success/40"
          }
        >
          <CardHeader>
            <div className="flex items-center justify-between gap-3">
              <CardTitle className="flex items-center gap-2">
                <ShieldCheck
                  className={
                    verification.status === "issue"
                      ? "size-4 text-warning"
                      : "size-4 text-success"
                  }
                />
                事实核验报告
              </CardTitle>
              <Badge
                variant={
                  verification.status === "issue"
                    ? "warning"
                    : verification.status === "pass"
                      ? "success"
                      : "muted"
                }
              >
                {verification.status === "issue"
                  ? "发现待核实内容"
                  : verification.status === "pass"
                    ? "已通过"
                    : "未核验"}
              </Badge>
            </div>
            <CardDescription>{verification.summary}</CardDescription>
          </CardHeader>
          {verification.issues.length > 0 ? (
            <CardContent className="flex flex-col gap-3">
              {verification.issues.map((issue) => (
                <div
                  key={issue.id}
                  className="flex flex-col gap-1 rounded-md border border-border p-3"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge
                      variant={
                        issue.severity === "high" ? "destructive" : issue.severity === "medium" ? "warning" : "muted"
                      }
                    >
                      {issue.severity === "high" ? "高" : issue.severity === "medium" ? "中" : "低"}
                    </Badge>
                    <span className="text-sm font-medium">
                      {ISSUE_TYPE_LABEL[issue.type]}
                    </span>
                    <Badge variant="outline">
                      {issue.origin === "rule" ? "规则" : "AI"}
                    </Badge>
                  </div>
                  <p className="text-sm">{issue.message}</p>
                  {issue.quote ? (
                    <p className="text-xs text-muted-foreground">原文：{issue.quote}</p>
                  ) : null}
                  {issue.suggestion ? (
                    <p className="text-xs text-primary">建议：{issue.suggestion}</p>
                  ) : null}
                </div>
              ))}
            </CardContent>
          ) : null}
        </Card>
      ) : null}

      <div className="flex flex-col gap-4">
        {draft.map((section, index) => (
          <div
            key={section.id}
            className={
              section.kind === "risk"
                ? "rounded-lg border border-warning/40 bg-warning/5 p-4"
                : "rounded-lg border border-border bg-card p-4"
            }
          >
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <Badge variant="outline">{KIND_LABEL[section.kind]}</Badge>
              <Badge variant={section.origin === "ai" ? "default" : "secondary"}>
                {section.origin === "ai" ? "AI" : "手动"}
              </Badge>
              <input
                value={section.title}
                onChange={(event) => updateSection(section.id, { title: event.target.value })}
                className="min-w-0 flex-1 rounded-md border border-transparent bg-transparent px-1 text-sm font-medium hover:border-border focus:border-input focus:outline-none"
                aria-label="段落标题"
              />
              <button
                type="button"
                onClick={() => handleRewrite(section)}
                aria-label="AI 改写"
                disabled={
                  rewritingId !== null ||
                  !/^[0-9a-f-]{36}$/i.test(section.id)
                }
                title={
                  !/^[0-9a-f-]{36}$/i.test(section.id)
                    ? "先保存为新版本，再对该段落使用 AI 改写"
                    : "AI 改写"
                }
                className="rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-primary disabled:opacity-50"
              >
                <Sparkles className="size-4" />
              </button>
              <button
                type="button"
                onClick={() => removeSection(section.id)}
                aria-label="删除段落"
                className="rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-destructive"
              >
                <Trash2 className="size-4" />
              </button>
            </div>
            <Textarea
              value={section.content}
              onChange={(event) => updateSection(section.id, { content: event.target.value })}
              rows={3}
              placeholder={`填写${KIND_LABEL[section.kind]}内容`}
              aria-label={KIND_LABEL[section.kind]}
            />
            {suggestion?.sectionId === section.id ? (
              <div className="mt-2 rounded-md border border-primary/40 bg-accent/40 p-3">
                <p className="text-xs font-medium text-primary">AI 改写建议</p>
                <p className="mt-1 text-sm">{suggestion.content}</p>
                <div className="mt-2 flex gap-2">
                  <Button size="sm" variant="outline" onClick={acceptSuggestion}>
                    <Check /> 采纳
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setSuggestion(null)}
                  >
                    <X /> 忽略
                  </Button>
                </div>
              </div>
            ) : null}
            <p className="mt-1 text-xs text-muted-foreground">第 {index + 1} 段</p>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <select
          value={newKind}
          onChange={(event) => setNewKind(event.target.value as ScriptSectionKind)}
          className={selectClass}
          aria-label="段落类型"
        >
          {Object.entries(KIND_LABEL).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <Button variant="outline" size="sm" onClick={addSection}>
          <Plus /> 添加段落
        </Button>
        <Button size="sm" onClick={saveVersion} disabled={saving}>
          <Save /> {saving ? "保存中…" : "保存为新版本"}
        </Button>
      </div>
    </div>
  );
}
