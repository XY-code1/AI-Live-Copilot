"use client";

import { ErrorBlock } from "@/components/common/state-blocks";

export default function Error({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="py-10">
      <ErrorBlock title="页面出错了" description="这个页面遇到了问题，请重试。" onRetry={reset} />
    </div>
  );
}
