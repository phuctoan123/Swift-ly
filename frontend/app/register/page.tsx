"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { LinkSimple, Eye, EyeSlash, CheckCircle } from "@phosphor-icons/react";
import { apiRegister } from "@/lib/api";

function validate(field: string, value: string): string | null {
  if (field === "email") {
    if (!value.includes("@")) return "Email không hợp lệ.";
  }
  if (field === "username") {
    if (value.length < 3) return "Username phải có ít nhất 3 ký tự.";
    if (!/^[a-zA-Z0-9_]+$/.test(value)) return "Chỉ dùng chữ, số và dấu gạch dưới.";
  }
  if (field === "password") {
    if (value.length < 8) return "Mật khẩu phải có ít nhất 8 ký tự.";
  }
  return null;
}

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", username: "", password: "" });
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const errors = {
    email: touched.email ? validate("email", form.email) : null,
    username: touched.username ? validate("username", form.username) : null,
    password: touched.password ? validate("password", form.password) : null,
  };
  const isValid = !errors.email && !errors.username && !errors.password
    && form.email && form.username && form.password;

  function handleChange(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }
  function handleBlur(field: string) {
    setTouched((prev) => ({ ...prev, [field]: true }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setTouched({ email: true, username: true, password: true });
    if (!isValid) return;
    setError(null);
    setLoading(true);
    try {
      await apiRegister(form);
      router.push("/login?registered=1");
    } catch (err: any) {
      let msg = "Đăng ký thất bại. Email hoặc username đã tồn tại.";
      if (err?.data?.detail) {
        msg = typeof err.data.detail === "string" ? err.data.detail : err.data.detail.message || msg;
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  function inputStyle(field: "email" | "username" | "password"): React.CSSProperties {
    if (!touched[field]) return {};
    const hasError = !!errors[field];
    const hasValue = !!form[field];
    if (hasError) return { borderColor: "var(--color-error)", boxShadow: "0 0 0 3px rgba(238,0,0,0.08)" };
    if (!hasError && hasValue) return { borderColor: "var(--color-success)", boxShadow: "0 0 0 3px rgba(0,112,243,0.08)" };
    return {};
  }

  function FieldIcon({ field }: { field: "email" | "username" | "password" }) {
    if (!touched[field] || !form[field] || errors[field]) return null;
    return (
      <span style={{ position: "absolute", right: "10px", top: "50%", transform: "translateY(-50%)" }}>
        <CheckCircle size={16} color="var(--color-success)" weight="fill" />
      </span>
    );
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
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "32px" }}>
          <div style={{
            width: "28px", height: "28px", background: "var(--color-ink)",
            borderRadius: "6px", display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <LinkSimple size={14} color="white" weight="bold" />
          </div>
          <span style={{ fontFamily: "'Geist Mono', monospace", fontWeight: 600, fontSize: "15px" }}>Short.ly</span>
        </div>

        <h1 style={{ fontSize: "24px", fontWeight: 600, letterSpacing: "-0.03em", marginBottom: "6px" }}>
          Tạo tài khoản
        </h1>
        <p style={{ fontSize: "14px", color: "var(--color-mute)", marginBottom: "28px" }}>
          Đã có tài khoản?{" "}
          <Link href="/login" style={{ color: "var(--color-link)", textDecoration: "none" }}>Đăng nhập</Link>
        </p>

        {error && (
          <div style={{
            padding: "10px 12px", marginBottom: "16px",
            background: "var(--color-error-soft)", border: "1px solid rgba(238,0,0,0.15)",
            borderRadius: "6px", fontSize: "13px", color: "var(--color-error-deep)",
          }}>{error}</div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {/* Email */}
          <div>
            <label style={{ fontSize: "13px", fontWeight: 500, display: "block", marginBottom: "6px" }}>Email</label>
            <div style={{ position: "relative" }}>
              <input
                type="email" value={form.email} placeholder="you@example.com"
                onChange={(e) => handleChange("email", e.target.value)}
                onBlur={() => handleBlur("email")}
                className="form-input" style={{ width: "100%", ...inputStyle("email") }}
              />
              <FieldIcon field="email" />
            </div>
            {errors.email && <p style={{ fontSize: "12px", color: "var(--color-error)", marginTop: "4px" }}>{errors.email}</p>}
          </div>

          {/* Username */}
          <div>
            <label style={{ fontSize: "13px", fontWeight: 500, display: "block", marginBottom: "6px" }}>Tên đăng nhập</label>
            <div style={{ position: "relative" }}>
              <input
                type="text" value={form.username} placeholder="your_username"
                onChange={(e) => handleChange("username", e.target.value)}
                onBlur={() => handleBlur("username")}
                className="form-input" style={{ width: "100%", ...inputStyle("username") }}
              />
              <FieldIcon field="username" />
            </div>
            {errors.username && <p style={{ fontSize: "12px", color: "var(--color-error)", marginTop: "4px" }}>{errors.username}</p>}
          </div>

          {/* Password */}
          <div>
            <label style={{ fontSize: "13px", fontWeight: 500, display: "block", marginBottom: "6px" }}>Mật khẩu</label>
            <div style={{ position: "relative" }}>
              <input
                type={showPw ? "text" : "password"} value={form.password} placeholder="Ít nhất 8 ký tự"
                onChange={(e) => handleChange("password", e.target.value)}
                onBlur={() => handleBlur("password")}
                className="form-input" style={{ width: "100%", paddingRight: "40px", ...inputStyle("password") }}
              />
              <button
                type="button" onClick={() => setShowPw(!showPw)}
                style={{ position: "absolute", right: "10px", top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "var(--color-mute)" }}
              >
                {showPw ? <EyeSlash size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.password && <p style={{ fontSize: "12px", color: "var(--color-error)", marginTop: "4px" }}>{errors.password}</p>}
          </div>

          <button
            type="submit" disabled={loading}
            className="btn-primary"
            style={{ width: "100%", marginTop: "8px", justifyContent: "center", opacity: !isValid ? 0.5 : 1 }}
          >
            {loading ? <><div className="spinner" />Đang tạo tài khoản...</> : "Tạo tài khoản"}
          </button>
        </form>
      </div>
    </div>
  );
}
