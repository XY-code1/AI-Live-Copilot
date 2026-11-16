import { FileText, Image as ImageIcon, Link2, PenLine } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { Card, CardContent } from "@/components/ui/card";

const channels: { label: string; description: string; icon: LucideIcon }[] = [
  { label: "PDF / 文档", description: "行程单、产品手册、合同", icon: FileText },
  { label: "图片 / 截图", description: "OCR 识别与多模态理解", icon: ImageIcon },
  { label: "商品链接", description: "自动抓取详情页信息", icon: Link2 },
  { label: "手动录入", description: "直接填写商品基础信息", icon: PenLine },
];

export default function ProductImportPage() {
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
            <Card key={channel.label} className="border-dashed">
              <CardContent className="flex items-start gap-4 p-5">
                <div className="flex size-10 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                  <Icon className="size-5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold">{channel.label}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {channel.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
      <p className="text-sm text-muted-foreground">
        P2 将实现真实解析：提取结果会保留来源页码与确认状态。
      </p>
    </div>
  );
}
