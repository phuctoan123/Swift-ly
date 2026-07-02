"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { List, X, LinkSimple, Sun, Moon } from "@phosphor-icons/react";

const NAV_LINKS = [
  { href: "/", label: "Tính năng" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "#", label: "Tài liệu API" },
];

export function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    setIsLoggedIn(!!localStorage.getItem("access_token"));
    const saved = localStorage.getItem("theme") as "light" | "dark" | null;
    if (saved) setTheme(saved);
  }, []);

  function toggleTheme() {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    localStorage.setItem("theme", next);
    document.documentElement.setAttribute("data-theme", next);
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/";
  }

  return (
    <header
      style={{
        position: "sticky", top: 0, zIndex: 50,
        height: "64px",
        background: "rgba(255,255,255,0.85)",
        backdropFilter: "blur(12px)",
        borderBottom: "1px solid var(--color-hairline)",
      }}
    >
      <div
        style={{
          maxWidth: "1200px", margin: "0 auto",
          height: "100%", padding: "0 24px",
          display: "flex", alignItems: "center", justifyContent: "space-between",
        }}
      >
        {/* Logo */}
        <Link href="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{
            width: "28px", height: "28px", background: "var(--color-ink)",
            borderRadius: "6px", display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <LinkSimple size={16} color="white" weight="bold" />
          </div>
          <span style={{
            fontFamily: "'Geist Mono', monospace", fontWeight: 600,
            fontSize: "15px", color: "var(--color-ink)",
          }}>
            Short.ly
          </span>
        </Link>

        {/* Center nav — desktop */}
        <nav style={{ display: "flex", gap: "2px" }} className="desktop-nav">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`nav-link${pathname === link.href ? " active" : ""}`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Right actions */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="btn-ghost"
            aria-label="Chuyển đổi giao diện"
            style={{ padding: "6px" }}
          >
            {theme === "light" ? <Moon size={16} /> : <Sun size={16} />}
          </button>

          {isLoggedIn ? (
            <>
              <Link href="/dashboard" className="btn-secondary" style={{ textDecoration: "none", fontSize: "13px" }}>
                Dashboard
              </Link>
              <button onClick={handleLogout} className="btn-secondary" style={{ fontSize: "13px" }}>
                Đăng xuất
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                style={{
                  textDecoration: "none", fontSize: "13px", fontWeight: 500,
                  color: "var(--color-ink)", padding: "4px 10px",
                  border: "1px solid var(--color-hairline)",
                  borderRadius: "6px",
                  transition: "background 150ms",
                }}
              >
                Đăng nhập
              </Link>
              <Link
                href="/register"
                style={{
                  textDecoration: "none", fontSize: "13px", fontWeight: 500,
                  color: "white", padding: "4px 10px",
                  background: "var(--color-ink)",
                  borderRadius: "6px",
                  transition: "background 150ms",
                }}
              >
                Đăng ký
              </Link>
            </>
          )}

          {/* Mobile hamburger */}
          <button
            className="btn-ghost"
            onClick={() => setMobileOpen(!mobileOpen)}
            style={{ display: "none", padding: "6px" }}
            aria-label="Menu"
          >
            {mobileOpen ? <X size={20} /> : <List size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div style={{
          position: "fixed", inset: 0, top: "64px",
          background: "var(--color-canvas)", zIndex: 40,
          padding: "24px",
          animation: "fade-in 0.2s ease both",
        }}>
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMobileOpen(false)}
              style={{
                display: "block", padding: "12px 0",
                fontSize: "18px", fontWeight: 500,
                color: "var(--color-ink)", textDecoration: "none",
                borderBottom: "1px solid var(--color-hairline)",
              }}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}

      <style>{`
        @media (max-width: 768px) {
          .desktop-nav { display: none !important; }
          button[aria-label="Menu"] { display: flex !important; }
        }
      `}</style>
    </header>
  );
}
