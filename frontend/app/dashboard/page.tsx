import type { Metadata } from "next";
import { UrlTable } from "@/components/dashboard/url-table";
import { ShortenForm } from "@/components/landing/shorten-form";

export const metadata: Metadata = { title: "Liên kết của tôi" };

export default function DashboardPage() {
  return (
    <div style={{ animation: "fade-up 0.5s cubic-bezier(0.16,1,0.3,1) both" }}>
      {/* Header */}
      <div style={{ marginBottom: "32px" }}>
        <h1 style={{ fontSize: "24px", fontWeight: 600, letterSpacing: "-0.03em", marginBottom: "6px" }}>
          Liên kết của tôi
        </h1>
        <p style={{ fontSize: "14px", color: "var(--color-mute)" }}>
          Quản lý và theo dõi tất cả liên kết rút gọn của bạn.
        </p>
      </div>

      {/* Quick shorten form */}
      <div style={{ marginBottom: "32px" }}>
        <ShortenForm />
      </div>

      {/* URL list */}
      <UrlTable />
    </div>
  );
}
