"use client";

import { ClerkProvider, useAuth } from "@clerk/nextjs";
import { useEffect } from "react";

import { setAccessTokenProvider } from "@/lib/api";

function TokenBridge({ children }: { children: React.ReactNode }) {
  const { getToken } = useAuth();
  useEffect(() => {
    setAccessTokenProvider(() => getToken());
    return () => setAccessTokenProvider(async () => null);
  }, [getToken]);
  return children;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  if (!publishableKey) return children;
  return (
    <ClerkProvider publishableKey={publishableKey}>
      <TokenBridge>{children}</TokenBridge>
    </ClerkProvider>
  );
}

