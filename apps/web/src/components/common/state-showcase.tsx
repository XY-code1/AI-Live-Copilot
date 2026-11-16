"use client";

import { useState } from "react";
import { Inbox } from "lucide-react";

import { EmptyState } from "@/components/common/empty-state";
import { ErrorBlock, LoadingBlock } from "@/components/common/state-blocks";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function StateShowcase() {
  const [retried, setRetried] = useState(false);

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle>空态</CardTitle>
          <CardDescription>无数据时的引导。</CardDescription>
        </CardHeader>
        <CardContent>
          <EmptyState
            icon={Inbox}
            title="暂无内容"
            description="当列表没有数据时展示，并提供下一步操作。"
            actionLabel="新建"
            onAction={() => undefined}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>加载态</CardTitle>
          <CardDescription>数据加载中。</CardDescription>
        </CardHeader>
        <CardContent>
          <LoadingBlock rows={3} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>错误态</CardTitle>
          <CardDescription>加载失败与重试。</CardDescription>
        </CardHeader>
        <CardContent>
          <ErrorBlock
            title="加载失败"
            description={retried ? "已触发重试（演示）。" : "出现了一些问题，请稍后重试。"}
            onRetry={() => setRetried(true)}
          />
        </CardContent>
      </Card>
    </div>
  );
}
