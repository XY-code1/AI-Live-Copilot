import { AppShell } from "@/components/layout/app-shell";

// The shared shell uses client hooks (usePathname) for navigation state,
// so it cannot be an instantly rendered segment.
export const instant = false;

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
