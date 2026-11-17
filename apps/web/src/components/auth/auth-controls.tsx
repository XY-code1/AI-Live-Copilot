"use client";

import { useRouter } from "next/navigation";

import { clearAuthToken } from "@/components/auth/auth-provider";
import { Button } from "@/components/ui/button";

export function AuthControls() {
  const router = useRouter();

  function logout() {
    clearAuthToken();
    router.push("/login");
    router.refresh();
  }

  return (
    <Button size="sm" variant="outline" onClick={logout}>
      退出
    </Button>
  );
}

