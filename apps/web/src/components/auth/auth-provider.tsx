"use client";

import { useEffect } from "react";

import { setAccessTokenProvider } from "@/lib/api";

export const AUTH_COOKIE = "ailc_token";

export function getAuthToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(
    new RegExp(`(?:^|;\\s*)${AUTH_COOKIE}=([^;]+)`),
  );
  return match ? decodeURIComponent(match[1]) : null;
}

export function setAuthToken(token: string) {
  document.cookie = `${AUTH_COOKIE}=${encodeURIComponent(token)}; path=/; max-age=${60 * 60 * 24 * 7}`;
}

export function clearAuthToken() {
  document.cookie = `${AUTH_COOKIE}=; path=/; max-age=0`;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    setAccessTokenProvider(async () => getAuthToken());
  }, []);
  return children;
}
