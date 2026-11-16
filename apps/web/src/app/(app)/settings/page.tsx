import { PageHeader } from "@/components/common/page-header";
import { StateShowcase } from "@/components/common/state-showcase";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { currentWorkspace } from "@/lib/mock-data";

export default function SettingsPage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="设置" description="工作空间、偏好与界面状态。" />

      <Card>
        <CardHeader>
          <CardTitle>工作空间</CardTitle>
          <CardDescription>P1 为演示数据，账号与权限将在 P6 实现。</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">名称</span>
            <span className="text-sm font-medium">{currentWorkspace.name}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">套餐</span>
            <Badge variant="secondary">{currentWorkspace.plan}</Badge>
          </div>
        </CardContent>
      </Card>

      <div className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold">界面状态</h2>
        <p className="text-sm text-muted-foreground">
          空态、加载态与错误态的统一规范，页面通过相同组件呈现。
        </p>
      </div>
      <StateShowcase />
    </div>
  );
}
