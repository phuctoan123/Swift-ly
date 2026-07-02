"use client";

import Link from "next/link";
import { LinkSimple } from "@phosphor-icons/react/dist/ssr";

const COLUMNS = [
  {
    label: "Sản phẩm",
    links: [
      { href: "/", label: "Rút gọn URL" },
      { href: "/dashboard", label: "Dashboard" },
      { href: "#", label: "Analytics" },
    ],
  },
  {
    label: "Tài nguyên",
    links: [
      { href: "http://localhost:8000/docs", label: "API Docs" },
      { href: "http://localhost:8000/redoc", label: "ReDoc" },
      { href: "#", label: "Changelog" },
    ],
  },
  {
    label: "Dự án",
    links: [
      { href: "#", label: "System Design" },
      { href: "#", label: "GitHub" },
      { href: "#", label: "Checklist" },
    ],
  },
];

export function Footer() {
  return (
    <footer style={{
      background: "var(--color-canvas)",
      borderTop: "1px solid var(--color-hairline)",
      padding: "64px 24px 40px",
    }}>
      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        {/* Top row */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr repeat(3, auto)",
          gap: "48px",
          marginBottom: "48px",
        }}>
          {/* Brand */}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
              <div style={{
                width: "24px", height: "24px", background: "var(--color-ink)",
                borderRadius: "5px", display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <LinkSimple size={13} color="white" weight="bold" />
              </div>
              <span style={{
                fontFamily: "'Geist Mono', monospace", fontWeight: 600,
                fontSize: "14px", color: "var(--color-ink)",
              }}>Short.ly</span>
            </div>
            <p style={{ fontSize: "13px", color: "var(--color-mute)", lineHeight: "1.6", maxWidth: "200px" }}>
              Rút gọn, theo dõi và quản lý liên kết của bạn.
            </p>
          </div>

          {/* Link columns */}
          {COLUMNS.map((col) => (
            <div key={col.label}>
              <p style={{
                fontFamily: "'Geist Mono', monospace",
                fontSize: "11px", fontWeight: 400,
                color: "var(--color-mute)", textTransform: "uppercase",
                letterSpacing: "0.08em", marginBottom: "12px",
              }}>
                {col.label}
              </p>
              <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "8px" }}>
                {col.links.map((link) => (
                  <li key={link.label}>
                    <Link href={link.href} style={{
                      fontSize: "13px", color: "var(--color-body)",
                      textDecoration: "none",
                      transition: "color 150ms",
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.color = "var(--color-ink)")}
                    onMouseLeave={(e) => (e.currentTarget.style.color = "var(--color-body)")}
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom row */}
        <div style={{
          borderTop: "1px solid var(--color-hairline)",
          paddingTop: "24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}>
          <p style={{ fontSize: "12px", color: "var(--color-mute)" }}>
            © 2026 Short.ly — Dự án học System Design
          </p>
          <p style={{
            fontFamily: "'Geist Mono', monospace",
            fontSize: "11px", color: "var(--color-mute)",
          }}>
            FastAPI · PostgreSQL · Redis · Next.js
          </p>
        </div>
      </div>
    </footer>
  );
}
