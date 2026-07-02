"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useShorten } from "@/hooks/use-shorten";
import { copyToClipboard } from "@/lib/utils";
import {
  Link as LinkIcon,
  CaretDown,
  CaretUp,
  Copy,
  Check,
  ArrowSquareOut,
  ChartBar,
  Warning,
} from "@phosphor-icons/react";
import type { APIError, ShortenResponse } from "@/types";

export function ShortenForm() {
  const router = useRouter();
  const { mutate, isPending } = useShorten();

  const [longUrl, setLongUrl] = useState("");
  const [customAlias, setCustomAlias] = useState("");
  const [expiresDays, setExpiresDays] = useState("");
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [result, setResult] = useState<ShortenResponse | null>(null);
  const [copied, setCopied] = useState(false);
  const [inlineError, setInlineError] = useState<{ field?: string; message: string; suggestion?: string } | null>(null);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  function showToast(msg: string) {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3000);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setInlineError(null);
    setResult(null);

    if (!longUrl.trim()) return;

    mutate(
      {
        long_url: longUrl.trim(),
        custom_alias: customAlias.trim() || undefined,
        expires_in_days: expiresDays ? parseInt(expiresDays) : undefined,
      },
      {
        onSuccess: (data) => {
          setResult(data);
          setLongUrl("");
          setCustomAlias("");
          setExpiresDays("");
          setAdvancedOpen(false);
        },
        onError: (err: any) => {
          const status = err.status;
          const data: APIError = err.data ?? {};

          if (status === 409) {
            setInlineError({
              field: "alias",
              message: data.message ?? "Alias này đã được sử dụng.",
              suggestion: data.suggestion,
            });
          } else if (status === 422) {
            setInlineError({ message: data.message ?? "URL không hợp lệ hoặc nằm trong danh sách cấm." });
          } else if (status === 429) {
            showToast("Bạn đang gửi quá nhiều yêu cầu. Vui lòng thử lại sau.");
          } else {
            setInlineError({ message: "Đã xảy ra lỗi. Vui lòng thử lại." });
          }
        },
      }
    );
  }

  async function handleCopy() {
    if (!result) return;
    const ok = await copyToClipboard(result.short_url);
    if (ok) {
      setCopied(true);
      showToast("Đã sao chép vào bộ nhớ tạm!");
      setTimeout(() => setCopied(false), 2000);
    }
  }

  const inputBorderStyle = inlineError && !inlineError.field
    ? "1px solid var(--color-error)"
    : "1px solid var(--color-hairline)";

  return (
    <div style={{ width: "100%", maxWidth: "640px", position: "relative" }}>
      {/* Toast */}
      {toastMsg && (
        <div style={{
          position: "fixed", bottom: "24px", left: "50%",
          transform: "translateX(-50%)",
          background: "var(--color-ink)", color: "white",
          padding: "10px 20px", borderRadius: "8px",
          fontSize: "13px", fontWeight: 500,
          boxShadow: "var(--shadow-4)",
          animation: "fade-up 0.3s ease",
          zIndex: 1000,
        }}>
          {toastMsg}
        </div>
      )}

      {/* Main form */}
      <form onSubmit={handleSubmit}>
        {/* URL Input row */}
        <div style={{
          display: "flex", gap: "8px", alignItems: "stretch",
          background: "var(--color-canvas)",
          border: inputBorderStyle,
          borderRadius: "10px",
          padding: "6px",
          boxShadow: "var(--shadow-3)",
          transition: "box-shadow 200ms, border-color 150ms",
        }}>
          <div style={{
            display: "flex", alignItems: "center",
            paddingLeft: "10px", color: "var(--color-mute)",
            flexShrink: 0,
          }}>
            <LinkIcon size={18} />
          </div>
          <input
            type="url"
            value={longUrl}
            onChange={(e) => { setLongUrl(e.target.value); setInlineError(null); }}
            placeholder="Dán URL dài của bạn vào đây..."
            required
            style={{
              flex: 1, border: "none", outline: "none",
              background: "transparent",
              fontSize: "15px", color: "var(--color-ink)",
              fontFamily: "inherit", padding: "8px 4px",
            }}
          />
          <button
            type="submit"
            disabled={isPending || !longUrl.trim()}
            className="btn-primary"
            style={{ flexShrink: 0, padding: "10px 20px", borderRadius: "7px", fontSize: "14px" }}
          >
            {isPending ? (
              <><div className="spinner" style={{ width: "14px", height: "14px" }} />Đang xử lý</>
            ) : "Rút gọn"}
          </button>
        </div>

        {/* Inline error: URL invalid / generic */}
        {inlineError && !inlineError.field && (
          <div style={{
            display: "flex", alignItems: "center", gap: "8px",
            marginTop: "8px", padding: "10px 12px",
            background: "var(--color-error-soft)",
            borderRadius: "6px", border: "1px solid rgba(238,0,0,0.15)",
          }}>
            <Warning size={15} color="var(--color-error)" weight="fill" />
            <span style={{ fontSize: "13px", color: "var(--color-error-deep)" }}>
              {inlineError.message}
            </span>
          </div>
        )}

        {/* Advanced options accordion */}
        <button
          type="button"
          onClick={() => setAdvancedOpen(!advancedOpen)}
          style={{
            display: "flex", alignItems: "center", gap: "4px",
            marginTop: "12px", background: "none", border: "none",
            cursor: "pointer", color: "var(--color-mute)",
            fontSize: "13px", padding: "0",
          }}
        >
          {advancedOpen ? <CaretUp size={14} /> : <CaretDown size={14} />}
          Tùy chọn nâng cao
        </button>

        {advancedOpen && (
          <div style={{
            marginTop: "10px", padding: "16px",
            background: "var(--color-canvas-soft)",
            border: "1px solid var(--color-hairline)",
            borderRadius: "8px",
            display: "flex", flexDirection: "column", gap: "12px",
            animation: "fade-up 0.2s ease both",
          }}>
            {/* Custom alias */}
            <div>
              <label style={{ fontSize: "12px", color: "var(--color-body)", display: "block", marginBottom: "6px" }}>
                Alias tùy chỉnh
              </label>
              <div style={{ position: "relative" }}>
                <span style={{
                  position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)",
                  fontSize: "13px", color: "var(--color-mute)", fontFamily: "'Geist Mono', monospace",
                }}>
                  short.ly/
                </span>
                <input
                  type="text"
                  value={customAlias}
                  onChange={(e) => { setCustomAlias(e.target.value); setInlineError(null); }}
                  placeholder="ten-cua-ban"
                  className={`form-input${inlineError?.field === "alias" ? " error" : ""}`}
                  style={{ paddingLeft: "72px" }}
                />
              </div>
              {inlineError?.field === "alias" && (
                <div style={{ marginTop: "6px", fontSize: "12px", color: "var(--color-error)" }}>
                  {inlineError.message}
                  {inlineError.suggestion && (
                    <button
                      type="button"
                      onClick={() => setCustomAlias(inlineError.suggestion!)}
                      style={{
                        marginLeft: "8px", color: "var(--color-link)",
                        background: "none", border: "none", cursor: "pointer", fontSize: "12px",
                        padding: 0, textDecoration: "underline",
                      }}
                    >
                      Dùng gợi ý: {inlineError.suggestion}
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Expiration */}
            <div>
              <label style={{ fontSize: "12px", color: "var(--color-body)", display: "block", marginBottom: "6px" }}>
                Hết hạn sau (ngày)
              </label>
              <select
                value={expiresDays}
                onChange={(e) => setExpiresDays(e.target.value)}
                className="form-input"
                style={{ appearance: "none", cursor: "pointer" }}
              >
                <option value="">Không hết hạn</option>
                <option value="1">1 ngày</option>
                <option value="7">7 ngày</option>
                <option value="30">30 ngày</option>
                <option value="90">90 ngày</option>
                <option value="365">1 năm</option>
              </select>
            </div>
          </div>
        )}
      </form>

      {/* Result card */}
      {result && (
        <div style={{
          marginTop: "20px",
          background: "var(--color-canvas)",
          border: "1px solid var(--color-hairline)",
          borderRadius: "10px",
          padding: "20px",
          boxShadow: "var(--shadow-3)",
          animation: "fade-up 0.4s cubic-bezier(0.16,1,0.3,1) both",
        }}>
          <p style={{ fontSize: "11px", color: "var(--color-mute)", marginBottom: "8px", fontFamily: "'Geist Mono', monospace", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            URL đã rút gọn
          </p>
          {/* Short URL display */}
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            padding: "10px 14px",
            background: "var(--color-canvas-soft)",
            borderRadius: "7px",
            border: "1px solid var(--color-hairline)",
            marginBottom: "12px",
          }}>
            <span style={{
              fontFamily: "'Geist Mono', monospace",
              fontSize: "15px", fontWeight: 600,
              color: "var(--color-link)",
            }}>
              {result.short_url}
            </span>
            <div style={{ display: "flex", gap: "6px" }}>
              <button onClick={handleCopy} className="btn-secondary" style={{ padding: "5px 10px", gap: "5px", fontSize: "12px" }}>
                {copied ? <Check size={13} weight="bold" color="var(--color-success)" /> : <Copy size={13} />}
                {copied ? "Đã sao chép" : "Sao chép"}
              </button>
              <a
                href={result.short_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary"
                style={{ padding: "5px 10px", textDecoration: "none", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "5px" }}
              >
                <ArrowSquareOut size={13} />
                Mở
              </a>
            </div>
          </div>

          {/* Original URL */}
          <p style={{ fontSize: "12px", color: "var(--color-mute)", marginBottom: "12px" }}>
            Liên kết gốc:{" "}
            <span style={{ color: "var(--color-body)" }}>
              {result.long_url.length > 60 ? result.long_url.slice(0, 60) + "…" : result.long_url}
            </span>
          </p>

          {/* Actions */}
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              onClick={() => router.push(`/dashboard/${result.short_code}/analytics`)}
              className="btn-secondary"
              style={{ fontSize: "13px", gap: "6px" }}
            >
              <ChartBar size={14} />
              Xem Analytics
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
