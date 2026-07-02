"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft } from "@phosphor-icons/react";
import { useAnalytics } from "@/hooks/use-analytics";
import { StatCards } from "@/components/analytics/stat-cards";
import { ClicksAreaChart } from "@/components/analytics/clicks-area-chart";
import { DevicePieChart } from "@/components/analytics/device-pie-chart";
import { TopCountriesTable } from "@/components/analytics/top-countries-table";

export default function AnalyticsPage({ params }: { params: Promise<{ code: string }> }) {
  const resolvedParams = use(params);
  const code = resolvedParams.code;
  const { data, isLoading, error } = useAnalytics(code);

  if (error) {
    return (
      <div style={{ padding: "40px 0", textAlign: "center" }}>
        <p style={{ color: "var(--color-error)", marginBottom: "16px" }}>
          Lỗi: Không thể tải dữ liệu phân tích.
        </p>
        <Link href="/dashboard" className="btn-secondary">
          <ArrowLeft size={16} /> Quay lại Dashboard
        </Link>
      </div>
    );
  }

  // Mock data for clicks over time since the backend API doesn't provide time-series data yet
  const mockTimeData = Array.from({ length: 7 }).map((_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (6 - i));
    return {
      date: d.toISOString(),
      clicks: Math.floor(Math.random() * (data?.total_clicks || 0) / 3) + 1,
    };
  });

  return (
    <div style={{ animation: "fade-up 0.5s cubic-bezier(0.16,1,0.3,1) both" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "32px" }}>
        <Link
          href="/dashboard"
          className="btn-ghost"
          style={{ padding: "8px", background: "var(--color-canvas)", border: "1px solid var(--color-hairline)" }}
        >
          <ArrowLeft size={16} />
        </Link>
        <div>
          <h1 style={{ fontSize: "24px", fontWeight: 600, letterSpacing: "-0.03em" }}>
            Analytics
          </h1>
          <p style={{ fontSize: "14px", color: "var(--color-mute)", fontFamily: "'Geist Mono', monospace" }}>
            /{code}
          </p>
        </div>
      </div>

      {/* Top Stats */}
      <div style={{ marginBottom: "32px" }}>
        <StatCards 
          totalClicks={data?.total_clicks ?? 0}
          devices={data?.devices ?? {}}
          countries={data?.countries ?? {}}
          isLoading={isLoading}
        />
      </div>

      {/* Charts Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: "24px" }}>
        {/* Main Chart: Clicks over time */}
        <div style={{
          background: "var(--color-canvas)",
          border: "1px solid var(--color-hairline)",
          borderRadius: "10px", padding: "24px",
          gridColumn: "1 / -1",
        }}>
          <h3 style={{ fontSize: "15px", fontWeight: 600, marginBottom: "24px" }}>
            Lượt click theo thời gian (7 ngày qua)
          </h3>
          {isLoading ? (
            <div className="skeleton" style={{ height: "300px", width: "100%", borderRadius: "8px" }} />
          ) : (
            <ClicksAreaChart data={mockTimeData} />
          )}
        </div>

        {/* Device breakdown */}
        <div style={{
          background: "var(--color-canvas)",
          border: "1px solid var(--color-hairline)",
          borderRadius: "10px", padding: "24px",
        }}>
          <h3 style={{ fontSize: "15px", fontWeight: 600, marginBottom: "24px" }}>
            Thiết bị
          </h3>
          {isLoading ? (
            <div className="skeleton" style={{ height: "300px", width: "100%", borderRadius: "50%" }} />
          ) : (
            <DevicePieChart data={data?.devices ?? {}} />
          )}
        </div>

        {/* Top Countries */}
        <div style={{
          background: "var(--color-canvas)",
          border: "1px solid var(--color-hairline)",
          borderRadius: "10px", padding: "24px",
        }}>
          <h3 style={{ fontSize: "15px", fontWeight: 600, marginBottom: "24px" }}>
            Quốc gia hàng đầu
          </h3>
          {isLoading ? (
            <div className="skeleton" style={{ height: "300px", width: "100%", borderRadius: "8px" }} />
          ) : (
            <TopCountriesTable data={data?.countries ?? {}} />
          )}
        </div>
      </div>
    </div>
  );
}
