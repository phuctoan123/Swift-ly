"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { LinkSimple, Eye, EyeSlash } from "@phosphor-icons/react";
import { apiLogin } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await apiLogin(username, password);
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      router.push("/dashboard");
    } catch (err: any) {
      let msg = "Tên đăng nhập hoặc mật khẩu không đúng.";
      if (err?.data?.detail) {
        msg = typeof err.data.detail === "string" ? err.data.detail : err.data.detail.message || msg;
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: "var(--color-canvas-soft)", padding: "24px",
    }}>
      <div style={{
        width: "100%", maxWidth: "400px",
        background: "var(--color-canvas)",
        border: "1px solid var(--color-hairline)",
        borderRadius: "12px", padding: "40px 32px",
        boxShadow: "var(--shadow-4)",
        animation: "fade-up 0.5s cubic-bezier(0.16,1,0.3,1) both",
      }}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "32px" }}>
          <div style={{
            width: "28px", height: "28px", background: "var(--color-ink)",
            borderRadius: "6px", display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <LinkSimple size={14} color="white" weight="bold" />
          </div>
          <span style={{ fontFamily: "'Geist Mono', monospace", fontWeight: 600, fontSize: "15px" }}>
            Short.ly
          </span>
        </div>

        <h1 style={{ fontSize: "24px", fontWeight: 600, letterSpacing: "-0.03em", marginBottom: "6px" }}>
          Đăng nhập
        </h1>
        <p style={{ fontSize: "14px", color: "var(--color-mute)", marginBottom: "28px" }}>
          Chưa có tài khoản?{" "}
          <Link href="/register" style={{ color: "var(--color-link)", textDecoration: "none" }}>
            Đăng ký ngay
          </Link>
        </p>

        {error && (
          <div style={{
            padding: "10px 12px", marginBottom: "16px",
            background: "var(--color-error-soft)",
            border: "1px solid rgba(238,0,0,0.15)",
            borderRadius: "6px",
            fontSize: "13px", color: "var(--color-error-deep)",
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {/* Username */}
          <div>
            <label style={{ fontSize: "13px", fontWeight: 500, display: "block", marginBottom: "6px" }}>
              Tên đăng nhập
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="your_username"
              required
              className="form-input"
              style={{ width: "100%" }}
            />
          </div>

          {/* Password */}
          <div>
            <label style={{ fontSize: "13px", fontWeight: 500, display: "block", marginBottom: "6px" }}>
              Mật khẩu
            </label>
            <div style={{ position: "relative" }}>
              <input
                type={showPw ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="form-input"
                style={{ width: "100%", paddingRight: "40px" }}
              />
              <button
                type="button"
                onClick={() => setShowPw(!showPw)}
                style={{
                  position: "absolute", right: "10px", top: "50%", transform: "translateY(-50%)",
                  background: "none", border: "none", cursor: "pointer",
                  color: "var(--color-mute)", padding: "2px",
                }}
              >
                {showPw ? <EyeSlash size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
            style={{ width: "100%", marginTop: "8px", justifyContent: "center" }}
          >
            {loading ? (
              <><div className="spinner" />Đang đăng nhập...</>
            ) : "Đăng nhập"}
          </button>
        </form>
      </div>
    </div>
  );
}
