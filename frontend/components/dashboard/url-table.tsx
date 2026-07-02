"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Copy, Trash, ChartLine, MagnifyingGlass, Funnel,
} from "@phosphor-icons/react";
import { useUrls, useDeleteUrl } from "@/hooks/use-urls";
import { copyToClipboard, truncateUrl, formatDate, isExpired } from "@/lib/utils";
import type { URLDetail } from "@/types";

function SkeletonRow() {
  return (
    <tr>
      {[180, 100, 260, 80, 80, 100].map((w, i) => (
        <td key={i} style={{ padding: "14px 12px", borderBottom: "1px solid var(--color-hairline)" }}>
          <div className="skeleton" style={{ height: "14px", width: `${w}px`, borderRadius: "4px" }} />
        </td>
      ))}
    </tr>
  );
}

function StatusBadge({ url }: { url: URLDetail }) {
  if (!url.is_active)
    return <span className="badge badge-inactive">Tắt</span>;
  if (isExpired(url.expires_at))
    return <span className="badge badge-error">Hết hạn</span>;
  return <span className="badge badge-active">Hoạt động</span>;
}

export function UrlTable() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "active" | "expired">("all");
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const { data, isLoading } = useUrls(50);
  const { mutate: deleteUrl, isPending: isDeleting } = useDeleteUrl();

  function showToast(msg: string) {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 2500);
  }

  async function handleCopy(url: URLDetail) {
    const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    await copyToClipboard(`${base}/${url.short_code}`);
    showToast("Đã sao chép liên kết!");
  }

  function handleDelete(code: string) {
    deleteUrl(code, {
      onSuccess: () => { setDeleteConfirm(null); showToast("Đã xóa liên kết."); },
    });
  }

  const items: URLDetail[] = data?.items ?? [];
  const filtered = items.filter((u) => {
    const matchSearch = u.short_code.includes(search) || u.long_url.toLowerCase().includes(search.toLowerCase());
    if (!matchSearch) return false;
    if (filter === "active") return u.is_active && !isExpired(u.expires_at);
    if (filter === "expired") return isExpired(u.expires_at);
    return true;
  });

  return (
    <div>
      {/* Toast */}
      {toastMsg && (
        <div style={{
          position: "fixed", bottom: "24px", left: "50%", transform: "translateX(-50%)",
          background: "var(--color-ink)", color: "white",
          padding: "10px 20px", borderRadius: "8px",
          fontSize: "13px", fontWeight: 500,
          boxShadow: "var(--shadow-4)", zIndex: 100,
          animation: "fade-up 0.3s ease",
        }}>{toastMsg}</div>
      )}

      {/* Delete dialog */}
      {deleteConfirm && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.3)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200,
        }}>
          <div style={{
            background: "var(--color-canvas)", borderRadius: "12px",
            padding: "32px", maxWidth: "380px", width: "100%",
            boxShadow: "var(--shadow-5)",
            animation: "fade-up 0.3s cubic-bezier(0.16,1,0.3,1) both",
          }}>
            <h3 style={{ fontSize: "17px", fontWeight: 600, marginBottom: "10px", letterSpacing: "-0.02em" }}>
              Xác nhận xóa liên kết
            </h3>
            <p style={{ fontSize: "14px", color: "var(--color-body)", marginBottom: "24px" }}>
              Hành động này không thể hoàn tác. Liên kết <code style={{ fontFamily: "'Geist Mono', monospace", color: "var(--color-ink)" }}>/{deleteConfirm}</code> sẽ bị xóa vĩnh viễn.
            </p>
            <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
              <button className="btn-secondary" onClick={() => setDeleteConfirm(null)}>Hủy</button>
              <button
                className="btn-primary"
                onClick={() => handleDelete(deleteConfirm)}
                disabled={isDeleting}
                style={{ background: "var(--color-error)", padding: "8px 16px" }}
              >
                {isDeleting ? "Đang xóa..." : "Xóa liên kết"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toolbar */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "16px", alignItems: "center" }}>
        <div style={{ position: "relative", flex: 1, maxWidth: "340px" }}>
          <MagnifyingGlass size={15} style={{
            position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)",
            color: "var(--color-mute)",
          }} />
          <input
            type="text" value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm kiếm URL hoặc alias..."
            className="form-input"
            style={{ paddingLeft: "34px" }}
          />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <Funnel size={14} color="var(--color-mute)" />
          {(["all", "active", "expired"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className="btn-ghost"
              style={{
                fontSize: "12px", padding: "4px 10px",
                background: filter === f ? "var(--color-canvas-soft-2)" : "transparent",
                color: filter === f ? "var(--color-ink)" : "var(--color-mute)",
                fontWeight: filter === f ? 500 : 400,
              }}
            >
              {f === "all" ? "Tất cả" : f === "active" ? "Hoạt động" : "Hết hạn"}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div style={{
        background: "var(--color-canvas)",
        border: "1px solid var(--color-hairline)",
        borderRadius: "10px",
        overflow: "hidden",
        boxShadow: "var(--shadow-2)",
      }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "var(--color-canvas-soft)" }}>
              {["ALIAS", "URL GỐC", "NGÀY TẠO", "TRẠNG THÁI", "HÀNH ĐỘNG"].map((h) => (
                <th key={h} style={{
                  padding: "10px 12px", textAlign: "left",
                  fontFamily: "'Geist Mono', monospace",
                  fontSize: "10px", fontWeight: 400,
                  color: "var(--color-mute)", letterSpacing: "0.08em",
                  borderBottom: "1px solid var(--color-hairline)",
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading
              ? Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
              : filtered.length === 0
              ? (
                <tr>
                  <td colSpan={5} style={{ padding: "48px", textAlign: "center" }}>
                    <p style={{ color: "var(--color-mute)", fontSize: "14px" }}>
                      {search ? "Không tìm thấy kết quả." : "Bạn chưa có liên kết nào."}
                    </p>
                  </td>
                </tr>
              )
              : filtered.map((url, idx) => (
                <tr
                  key={url.id}
                  style={{
                    borderBottom: "1px solid var(--color-hairline)",
                    animation: `fade-up 0.4s cubic-bezier(0.16,1,0.3,1) ${idx * 40}ms both`,
                    transition: "background 150ms",
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-canvas-soft)")}
                  onMouseLeave={(e) => (e.currentTarget.style.background = "")}
                >
                  <td style={{ padding: "14px 12px" }}>
                    <span style={{
                      fontFamily: "'Geist Mono', monospace",
                      fontSize: "13px", fontWeight: 600,
                      color: "var(--color-link)",
                    }}>/{url.short_code}</span>
                  </td>
                  <td style={{ padding: "14px 12px", maxWidth: "300px" }}>
                    <span style={{ fontSize: "13px", color: "var(--color-body)" }}>
                      {truncateUrl(url.long_url, 55)}
                    </span>
                  </td>
                  <td style={{ padding: "14px 12px" }}>
                    <span style={{ fontSize: "12px", color: "var(--color-mute)", fontFamily: "'Geist Mono', monospace" }}>
                      {formatDate(url.created_at)}
                    </span>
                  </td>
                  <td style={{ padding: "14px 12px" }}>
                    <StatusBadge url={url} />
                  </td>
                  <td style={{ padding: "14px 12px" }}>
                    <div style={{ display: "flex", gap: "4px" }}>
                      <button
                        onClick={() => handleCopy(url)}
                        className="btn-ghost"
                        style={{ padding: "5px 8px" }}
                        title="Sao chép"
                      >
                        <Copy size={14} />
                      </button>
                      <button
                        onClick={() => router.push(`/dashboard/${url.short_code}/analytics`)}
                        className="btn-ghost"
                        style={{ padding: "5px 8px" }}
                        title="Analytics"
                      >
                        <ChartLine size={14} />
                      </button>
                      <button
                        onClick={() => setDeleteConfirm(url.short_code)}
                        className="btn-ghost"
                        style={{ padding: "5px 8px", color: "var(--color-error)" }}
                        title="Xóa"
                      >
                        <Trash size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            }
          </tbody>
        </table>
      </div>

      {data && (
        <p style={{ fontSize: "12px", color: "var(--color-mute)", marginTop: "12px" }}>
          Hiển thị {filtered.length} / {data.total} liên kết
        </p>
      )}
    </div>
  );
}
