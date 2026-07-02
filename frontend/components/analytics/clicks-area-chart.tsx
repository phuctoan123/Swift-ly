"use client";

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { formatDate, formatCount } from "@/lib/utils";

interface ClicksAreaChartProps {
  data: { date: string; clicks: number }[];
}

export function ClicksAreaChart({ data }: ClicksAreaChartProps) {
  if (!data || data.length === 0) {
    return (
      <div style={{ height: "300px", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <p style={{ color: "var(--color-mute)", fontSize: "14px" }}>Không có dữ liệu click</p>
      </div>
    );
  }

  return (
    <div style={{ height: "300px", width: "100%" }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorClicks" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--color-link)" stopOpacity={0.3} />
              <stop offset="95%" stopColor="var(--color-link)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-hairline)" />
          <XAxis 
            dataKey="date" 
            axisLine={false} 
            tickLine={false} 
            tickFormatter={(val) => formatDate(val).substring(0, 5)} 
            tick={{ fontSize: 12, fill: "var(--color-mute)" }}
            dy={10}
          />
          <YAxis 
            axisLine={false} 
            tickLine={false} 
            tickFormatter={formatCount}
            tick={{ fontSize: 12, fill: "var(--color-mute)" }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: "var(--color-canvas)",
              borderColor: "var(--color-hairline)",
              borderRadius: "8px",
              boxShadow: "var(--shadow-3)",
              fontSize: "13px"
            }}
            labelFormatter={(label) => formatDate(label as string)}
            itemStyle={{ color: "var(--color-ink)", fontWeight: 500 }}
          />
          <Area 
            type="monotone" 
            dataKey="clicks" 
            stroke="var(--color-link)" 
            strokeWidth={2}
            fillOpacity={1} 
            fill="url(#colorClicks)" 
            name="Lượt click"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
