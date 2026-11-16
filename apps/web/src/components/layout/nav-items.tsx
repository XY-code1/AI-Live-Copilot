import {
  BarChart3,
  FolderOpen,
  LayoutDashboard,
  Library,
  Settings,
  Sparkles,
  Upload,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export type NavItem = {
  label: string;
  href: string;
  icon: LucideIcon;
};

export const mainNav: NavItem[] = [
  { label: "工作台", href: "/dashboard", icon: LayoutDashboard },
  { label: "商品知识库", href: "/products", icon: Library },
  { label: "竞品分析", href: "/analysis", icon: BarChart3 },
  { label: "话术工作台", href: "/scripts", icon: Sparkles },
  { label: "内容资产", href: "/assets", icon: FolderOpen },
];

export const secondaryNav: NavItem[] = [
  { label: "商品导入", href: "/products/import", icon: Upload },
  { label: "设置", href: "/settings", icon: Settings },
];

