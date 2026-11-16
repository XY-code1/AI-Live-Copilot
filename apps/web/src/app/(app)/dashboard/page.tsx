import Link from "next/link";
import {
  ArrowUpRight,
  BarChart3,
  FolderOpen,
  Library,
  Sparkles,
  Upload,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { PageHeader } from "@/components/common/page-header";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/format";
import { products, recentTasks, scripts } from "@/lib/mock-data";
import type { TaskStatus } from "@/types";

const quickLinks: { label: string; description: string; href: string; icon: LucideIcon }[] = [
  {
    label: "商品知识库",
    description: "查看与管理已导入的商品",
    href: "/products",
    icon: Library,
  },
  {
    label: "商品导入",
    description: "PDF、图片、链接或手动录入",
    href: "/products/import",
    icon: Upload,
  },
  {
    label: "竞品分析",
    description: "对比差异，提取优势",
    href: "/analysis",
    icon: BarChart3,
  },
  {
    label: "话术工作台",
    description: "生成与编辑直播话术",
    href: "/scripts",
    icon: Sparkles,
  },
  {
    label: "内容资产",
    description: "历史分析与话术版本",
    href: "/assets",
    icon: FolderOpen,
  },
];

const taskStatus: Record<TaskStatus, { label: string; variant: "success" | "warning" | "muted" | "destructive" }> = {
  done: { label: "已完成", variant: "success" },
  running: { label: "进行中", variant: "warning" },
  pending: { label: "待处理", variant: "muted" },
  failed: { label: "失败", variant: "destructive" },
};

export default function DashboardPage() {
  const unconfirmed = products.reduce(
    (count, product) =>
      count +
      product.attributes.filter((attribute) => attribute.status !== "confirmed").length,
    0,
  );
  const runningTasks = recentTasks.filter((task) => task.status === "running").length;

  const stats = [
    { label: "商品总数", value: products.length, hint: "已导入商品" },
    { label: "待确认属性", value: unconfirmed, hint: "需要人工核实" },
    { label: "进行中任务", value: runningTasks, hint: "解析 / 识别" },
    { label: "话术草稿", value: scripts.length, hint: "含待核实内容" },
  ];

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="工作台"
        description="查看近期任务与业务入口。"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardHeader className="gap-1 p-4">
              <CardDescription>{stat.label}</CardDescription>
              <CardTitle className="text-2xl">{stat.value}</CardTitle>
              <p className="text-xs text-muted-foreground">{stat.hint}</p>
            </CardHeader>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {quickLinks.map((link) => {
          const Icon = link.icon;
          return (
            <Link
              key={link.href}
              href={link.href}
              className="group rounded-lg border border-border bg-card p-4 transition-colors hover:border-primary/40 hover:bg-accent/40"
            >
              <div className="flex items-start justify-between">
                <div className="flex size-9 items-center justify-center rounded-md bg-primary/10 text-primary">
                  <Icon className="size-4" />
                </div>
                <ArrowUpRight className="size-4 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
              </div>
              <h3 className="mt-3 text-sm font-semibold">{link.label}</h3>
              <p className="mt-1 text-xs text-muted-foreground">{link.description}</p>
            </Link>
          );
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>最近任务</CardTitle>
          <CardDescription>解析、识别与生成的进度。</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col divide-y divide-border">
          {recentTasks.map((task) => {
            const status = taskStatus[task.status];
            return (
              <div key={task.id} className="flex items-center justify-between gap-4 py-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{task.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatDate(task.createdAt)}
                  </p>
                </div>
                <Badge variant={status.variant}>{status.label}</Badge>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}
