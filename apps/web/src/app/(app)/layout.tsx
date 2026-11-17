import { auth } from "@clerk/nextjs/server";

import { AppShell } from "@/components/layout/app-shell";

// The shared shell uses client hooks (usePathname) for navigation state,
// so it cannot be an instantly rendered segment.
export const instant = false;

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  if (process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) await auth.protect();
  return <AppShell>{children}</AppShell>;
}
