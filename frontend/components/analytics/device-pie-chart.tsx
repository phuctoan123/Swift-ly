"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

interface DevicePieChartProps {
  data: Record<string, number>;
}

const COLORS: Record<string, string> = {
  mobile: "#0070f3",  // Link blue
  desktop: "#171717", // Ink
  tablet: "#888888",  // Mute
  other: "#ebebeb",   // Hairline
};

const LABELS: Record<string, string> = {
  mobile: "Điện thoại",
  desktop: "Máy tính",
  tablet: "Máy tính bảng",
  other: "Khác",
};

export function DevicePieChart({ data }: DevicePieChartProps) {
  const chartData = Object.entries(data)
    .map(([key, value]) => ({
      name: key,
      label: LABELS[key] || key,
      value,
    }))
    .sort((a, b) => b.value - a.value);

  if (!chartData.length) {
    return (
      <div style={{ height: "300px", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <p style={{ color: "var(--color-mute)", fontSize: "14px" }}>Không có dữ liệu thiết bị</p>
      </div>
    );
  }

  return (
    <div style={{ height: "300px", width: "100%" }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name] || COLORS.other} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: any) => [`${value} lượt`, "Clicks"]}
            contentStyle={{
              backgroundColor: "var(--color-canvas)",
              borderColor: "var(--color-hairline)",
              borderRadius: "8px",
              boxShadow: "var(--shadow-3)",
              fontSize: "13px"
            }}
          />
          <Legend 
            verticalAlign="bottom" 
            height={36} 
            iconType="circle"
            formatter={(value, entry: any) => {
              const item = chartData.find(d => d.name === entry.payload.name);
              return <span style={{ color: "var(--color-body)", fontSize: "13px" }}>{item?.label || value}</span>;
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
