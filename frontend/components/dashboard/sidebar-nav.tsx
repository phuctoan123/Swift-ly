"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LinkSimple, ChartLine, Gear, Book } from "@phosphor-icons/react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Liên kết của tôi", icon: LinkSimple },
  { href: "/dashboard/analytics", label: "Analytics", icon: ChartLine },
  { href: "#", label: "Tài liệu API", icon: Book },
  { href: "#", label: "Cài đặt", icon: Gear },
];

export function SidebarNav() {
  const pathname = usePathname();

  return (
    <aside style={{
      width: "220px", flexShrink: 0,
      borderRight: "1px solid var(--color-hairline)",
      background: "var(--color-canvas)",
      padding: "24px 12px",
      display: "flex", flexDirection: "column", gap: "4px",
    }}>
      {NAV_ITEMS.map((item) => {
        const Icon = item.icon;
        const isActive = pathname === item.href;
        return (
          <Link
            key={item.label}
            href={item.href}
            style={{
              display: "flex", alignItems: "center", gap: "10px",
              padding: "8px 10px",
              borderRadius: "6px",
              textDecoration: "none",
              fontSize: "14px", fontWeight: isActive ? 500 : 400,
              color: isActive ? "var(--color-ink)" : "var(--color-body)",
              background: isActive ? "var(--color-canvas-soft-2)" : "transparent",
              position: "relative",
              transition: "background 150ms, color 150ms",
            }}
          >
            {isActive && (
              <span style={{
                position: "absolute", left: 0, top: "6px", bottom: "6px",
                width: "2px", background: "var(--color-ink)",
                borderRadius: "0 2px 2px 0",
              }} />
            )}
            <Icon size={16} weight={isActive ? "duotone" : "regular"} />
            {item.label}
          </Link>
        );
      })}
    </aside>
  );
}
