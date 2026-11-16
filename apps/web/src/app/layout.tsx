import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Live Copilot",
  description: "AI 直播带货内容智能平台",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
