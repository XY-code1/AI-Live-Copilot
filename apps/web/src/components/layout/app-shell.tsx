"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, PackageOpen, Search, X } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import { mainNav, secondaryNav } from "./nav-items";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { currentWorkspace } from "@/lib/mock-data";

function NavLink({
  item,
  onNavigate,
}: {
  item: { label: string; href: string; icon: LucideIcon };
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const active =
    item.href === "/dashboard"
      ? pathname === item.href
      : pathname === item.href || pathname.startsWith(`${item.href}/`);
  const Icon = item.icon;

  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      aria-current={active ? "page" : undefined}
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
        active
          ? "bg-accent text-accent-foreground"
          : "text-muted-foreground hover:bg-accent/60 hover:text-accent-foreground",
      )}
    >
      <Icon className="size-4" />
      <span>{item.label}</span>
    </Link>
  );
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-14 items-center gap-2 border-b border-border px-4">
        <div className="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
          <PackageOpen className="size-4" />
        </div>
        <span className="text-sm font-semibold">AI Live Copilot</span>
      </div>
      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto p-3">
        {mainNav.map((item) => (
          <NavLink key={item.href} item={item} onNavigate={onNavigate} />
        ))}
        <div className="my-2 border-t border-border" />
        {secondaryNav.map((item) => (
          <NavLink key={item.href} item={item} onNavigate={onNavigate} />
        ))}
      </nav>
      <div className="border-t border-border p-3">
        <p className="px-3 text-xs text-muted-foreground">
          演示数据 · P1 页面框架
        </p>
      </div>
    </div>
  );
}

function Topbar({ onOpenSidebar }: { onOpenSidebar: () => void }) {
  return (
    <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur">
      <button
        type="button"
        onClick={onOpenSidebar}
        aria-label="打开导航"
        className="rounded-md p-2 text-muted-foreground hover:bg-accent md:hidden"
      >
        <Menu className="size-5" />
      </button>

      <div className="flex min-w-0 items-center gap-2">
        <span className="truncate text-sm font-medium">{currentWorkspace.name}</span>
        <Badge variant="secondary" className="hidden sm:inline-flex">
          {currentWorkspace.plan}
        </Badge>
      </div>

      <div className="ml-auto flex items-center gap-2">
        <button
          type="button"
          aria-label="搜索"
          className="hidden size-9 items-center justify-center rounded-md text-muted-foreground hover:bg-accent sm:inline-flex"
        >
          <Search className="size-4" />
        </button>
        <Avatar className="size-8">
          <AvatarFallback>直</AvatarFallback>
        </Avatar>
      </div>
    </header>
  );
}

function AppShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="hidden w-60 shrink-0 border-r border-border bg-card md:block">
        <SidebarContent />
      </aside>

      {sidebarOpen ? (
        <div className="fixed inset-0 z-30 md:hidden">
          <div
            className="absolute inset-0 bg-foreground/40"
            aria-hidden
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="absolute inset-y-0 left-0 w-64 border-r border-border bg-card shadow-lg">
            <button
              type="button"
              onClick={() => setSidebarOpen(false)}
              aria-label="关闭导航"
              className="absolute right-3 top-3 rounded-md p-1 text-muted-foreground hover:bg-accent"
            >
              <X className="size-5" />
            </button>
            <SidebarContent onNavigate={() => setSidebarOpen(false)} />
          </aside>
        </div>
      ) : null}

      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar onOpenSidebar={() => setSidebarOpen(true)} />
        <main className="flex-1 p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}

export { AppShell };
