"use client";

import { formatCount } from "@/lib/utils";

interface TopCountriesTableProps {
  data: Record<string, number>;
}

// Simple map for country codes to names
const COUNTRY_NAMES: Record<string, string> = {
  vn: "Việt Nam",
  us: "Hoa Kỳ",
  jp: "Nhật Bản",
  kr: "Hàn Quốc",
  sg: "Singapore",
  gb: "Vương quốc Anh",
  fr: "Pháp",
  de: "Đức",
  au: "Úc",
  ca: "Canada",
};

export function TopCountriesTable({ data }: TopCountriesTableProps) {
  const chartData = Object.entries(data)
    .map(([code, clicks]) => ({
      code: code.toLowerCase(),
      name: COUNTRY_NAMES[code.toLowerCase()] || code.toUpperCase(),
      clicks,
    }))
    .sort((a, b) => b.clicks - a.clicks)
    .slice(0, 10); // Top 10

  const maxClicks = chartData.length > 0 ? chartData[0].clicks : 1;

  if (!chartData.length) {
    return (
      <div style={{ height: "300px", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <p style={{ color: "var(--color-mute)", fontSize: "14px" }}>Không có dữ liệu quốc gia</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "0 8px" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left", padding: "12px 0", color: "var(--color-mute)", fontSize: "12px", fontWeight: 500 }}>Quốc gia</th>
            <th style={{ textAlign: "right", padding: "12px 0", color: "var(--color-mute)", fontSize: "12px", fontWeight: 500 }}>Clicks</th>
          </tr>
        </thead>
        <tbody>
          {chartData.map((item, index) => (
            <tr key={item.code} style={{ borderTop: "1px solid var(--color-hairline)" }}>
              <td style={{ padding: "12px 0", display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ 
                  display: "inline-block", width: "18px", 
                  color: "var(--color-mute)", fontSize: "12px", 
                  fontFamily: "'Geist Mono', monospace" 
                }}>
                  {index + 1}.
                </span>
                <span style={{ fontSize: "14px", color: "var(--color-ink)", fontWeight: 500 }}>
                  {item.name}
                </span>
              </td>
              <td style={{ padding: "12px 0", textAlign: "right" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: "12px" }}>
                  <div style={{ width: "80px", height: "6px", background: "var(--color-canvas-soft-2)", borderRadius: "3px", overflow: "hidden" }}>
                    <div 
                      style={{ 
                        height: "100%", 
                        width: `${(item.clicks / maxClicks) * 100}%`,
                        background: "var(--color-link)",
                        borderRadius: "3px"
                      }} 
                    />
                  </div>
                  <span style={{ fontSize: "13px", color: "var(--color-body)", fontFamily: "'Geist Mono', monospace", width: "40px" }}>
                    {formatCount(item.clicks)}
                  </span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
