import { SidebarNav } from "@/components/dashboard/sidebar-nav";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Dashboard" };

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      display: "flex",
      minHeight: "calc(100vh - 64px)",
      background: "var(--color-canvas-soft)",
    }}>
      <SidebarNav />
      <main style={{ flex: 1, padding: "32px", overflow: "auto" }}>
        {children}
      </main>
    </div>
  );
}
