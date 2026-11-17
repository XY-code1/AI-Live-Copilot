"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { authApi } from "@/lib/api";
import { setAuthToken } from "@/components/auth/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const result =
        mode === "register"
          ? await authApi.register({ email, password, name: name || undefined })
          : await authApi.login({ email, password });
      setAuthToken(result.token);
      router.push("/dashboard");
      router.refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "操作失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-sm rounded-lg border border-border bg-card p-6 shadow-sm">
        <h1 className="text-lg font-semibold">AI Live Copilot</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {mode === "login" ? "登录你的账号" : "创建账号，自动加入工作区"}
        </p>
        <form onSubmit={submit} className="mt-4 flex flex-col gap-3">
          {mode === "register" ? (
            <div className="flex flex-col gap-2">
              <Label htmlFor="name">昵称</Label>
              <Input
                id="name"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="可选"
              />
            </div>
          ) : null}
          <div className="flex flex-col gap-2">
            <Label htmlFor="email">邮箱</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="password">密码</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={mode === "register" ? 8 : 1}
            />
          </div>
          {error ? (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}
          <Button type="submit" disabled={busy}>
            {busy ? "请稍候…" : mode === "login" ? "登录" : "注册"}
          </Button>
        </form>
        <button
          type="button"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          className="mt-3 text-sm text-primary hover:underline"
        >
          {mode === "login" ? "没有账号？注册" : "已有账号？登录"}
        </button>
      </div>
    </div>
  );
}
