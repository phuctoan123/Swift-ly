"use client";

import { formatCount } from "@/lib/utils";
import { CursorClick, Users, DeviceMobile, Globe } from "@phosphor-icons/react";

interface StatCardsProps {
  totalClicks: number;
  devices: Record<string, number>;
  countries: Record<string, number>;
  isLoading: boolean;
}

function SkeletonCard() {
  return (
    <div style={{
      background: "var(--color-canvas)",
      border: "1px solid var(--color-hairline)",
      borderRadius: "10px", padding: "24px",
      boxShadow: "var(--shadow-2)",
    }}>
      <div className="skeleton" style={{ height: "12px", width: "80px", borderRadius: "4px", marginBottom: "16px" }} />
      <div className="skeleton" style={{ height: "32px", width: "60px", borderRadius: "6px", marginBottom: "8px" }} />
      <div className="skeleton" style={{ height: "11px", width: "100px", borderRadius: "4px" }} />
    </div>
  );
}

export function StatCards({ totalClicks, devices, countries, isLoading }: StatCardsProps) {
  if (isLoading) {
    return (
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px" }}>
        {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
      </div>
    );
  }

  const mobileClicks = devices["mobile"] ?? 0;
  const mobileRate = totalClicks > 0 ? Math.round((mobileClicks / totalClicks) * 100) : 0;
  const topCountry = Object.entries(countries).sort((a, b) => b[1] - a[1])[0];
  const uniqueIPs = Object.values(countries).reduce((a, b) => a + b, 0);

  const STATS = [
    {
      label: "Tổng lượt click",
      value: formatCount(totalClicks),
      sub: "Tất cả thời gian",
      icon: CursorClick,
      color: "var(--color-link)",
      bg: "var(--color-link-bg-soft)",
    },
    {
      label: "Unique IPs",
      value: formatCount(uniqueIPs),
      sub: "Ước tính từ countries",
      icon: Users,
      color: "#7928ca",
      bg: "#f3eafe",
    },
    {
      label: "Tỷ lệ Mobile",
      value: `${mobileRate}%`,
      sub: `${formatCount(mobileClicks)} lượt từ mobile`,
      icon: DeviceMobile,
      color: "#29bc9b",
      bg: "#edfaf6",
    },
    {
      label: "Quốc gia hàng đầu",
      value: topCountry ? topCountry[0].toUpperCase() : "—",
      sub: topCountry ? `${formatCount(topCountry[1])} lượt click` : "Chưa có dữ liệu",
      icon: Globe,
      color: "#f5a623",
      bg: "#fffbeb",
    },
  ];

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
      gap: "16px",
    }}
    className="stagger">
      {STATS.map((stat) => {
        const Icon = stat.icon;
        return (
          <div
            key={stat.label}
            style={{
              background: "var(--color-canvas)",
              border: "1px solid var(--color-hairline)",
              borderRadius: "10px", padding: "24px",
              boxShadow: "var(--shadow-2)",
              transition: "box-shadow 200ms, transform 200ms",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLDivElement).style.boxShadow = "var(--shadow-3)";
              (e.currentTarget as HTMLDivElement).style.transform = "translateY(-1px)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLDivElement).style.boxShadow = "var(--shadow-2)";
              (e.currentTarget as HTMLDivElement).style.transform = "";
            }}
          >
            <div style={{
              display: "flex", justifyContent: "space-between", alignItems: "flex-start",
              marginBottom: "16px",
            }}>
              <span style={{
                fontFamily: "'Geist Mono', monospace",
                fontSize: "10px", color: "var(--color-mute)",
                textTransform: "uppercase", letterSpacing: "0.08em",
              }}>
                {stat.label}
              </span>
              <div style={{
                width: "30px", height: "30px",
                background: stat.bg,
                borderRadius: "7px",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <Icon size={15} color={stat.color} weight="duotone" />
              </div>
            </div>
            <p style={{
              fontSize: "32px", fontWeight: 600,
              color: "var(--color-ink)", letterSpacing: "-0.04em",
              lineHeight: 1, marginBottom: "6px",
            }}>
              {stat.value}
            </p>
            <p style={{ fontSize: "12px", color: "var(--color-mute)" }}>
              {stat.sub}
            </p>
          </div>
        );
      })}
    </div>
  );
}
