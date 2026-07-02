import { ShortenForm } from "@/components/landing/shorten-form";
import { ChartLine, Lock, Gauge } from "@phosphor-icons/react/dist/ssr";

const FEATURES = [
  {
    icon: Gauge,
    title: "Tốc độ redirect < 100ms",
    desc: "Được tối ưu với Redis cache và PostgreSQL index để đảm bảo độ trễ thấp nhất.",
  },
  {
    icon: ChartLine,
    title: "Analytics thời gian thực",
    desc: "Theo dõi lượt click, thiết bị, quốc gia và nguồn giới thiệu cho mỗi liên kết.",
  },
  {
    icon: Lock,
    title: "Bảo mật hệ thống",
    desc: "Chặn SSRF, domain đen, rate limiting và xác thực JWT cho mọi tài khoản.",
  },
];

export function HeroSection() {
  return (
    <section style={{ position: "relative", overflow: "hidden" }}>
      {/* Mesh gradient backdrop */}
      <div className="mesh-gradient" />

      {/* Content */}
      <div style={{
        position: "relative", zIndex: 1,
        maxWidth: "1200px", margin: "0 auto",
        padding: "96px 24px 80px",
        display: "flex", flexDirection: "column", alignItems: "center",
        textAlign: "center",
      }}>
        {/* Eyebrow label */}
        <div style={{
          display: "inline-flex", alignItems: "center", gap: "8px",
          background: "var(--color-canvas-soft)",
          border: "1px solid var(--color-hairline)",
          borderRadius: "9999px",
          padding: "4px 12px",
          marginBottom: "32px",
          animation: "fade-up 0.5s cubic-bezier(0.16,1,0.3,1) 0ms both",
        }}>
          <span style={{
            fontFamily: "'Geist Mono', monospace",
            fontSize: "11px", color: "var(--color-mute)",
            textTransform: "uppercase", letterSpacing: "0.08em",
          }}>
            URL Shortener — System Design Project
          </span>
        </div>

        {/* Headline */}
        <h1
          style={{
            fontSize: "clamp(36px, 6vw, 56px)",
            fontWeight: 600, lineHeight: 1.05,
            letterSpacing: "-0.04em",
            color: "var(--color-ink)",
            marginBottom: "20px", maxWidth: "720px",
            animation: "fade-up 0.6s cubic-bezier(0.16,1,0.3,1) 80ms both",
          }}
        >
          Rút gọn liên kết.{" "}
          <br />
          <span style={{ color: "var(--color-mute)", fontWeight: 400 }}>
            Theo dõi mọi lượt click.
          </span>
        </h1>

        {/* Subtext */}
        <p style={{
          fontSize: "18px", color: "var(--color-body)",
          lineHeight: 1.6, maxWidth: "480px",
          marginBottom: "48px",
          animation: "fade-up 0.6s cubic-bezier(0.16,1,0.3,1) 160ms both",
        }}>
          Chuyển đường dẫn dài thành link ngắn gọn. Tích hợp analytics, custom alias và kiểm soát thời hạn.
        </p>

        {/* Form */}
        <div style={{
          width: "100%",
          animation: "fade-up 0.6s cubic-bezier(0.16,1,0.3,1) 240ms both",
        }}>
          <ShortenForm />
        </div>
      </div>

      {/* Feature strip */}
      <div style={{
        borderTop: "1px solid var(--color-hairline)",
        background: "var(--color-canvas)",
      }}>
        <div style={{
          maxWidth: "1200px", margin: "0 auto",
          padding: "64px 24px",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: "1px",
          background: "var(--color-hairline)",
        }}>
          {FEATURES.map((feat, i) => {
            const Icon = feat.icon;
            return (
              <div
                key={feat.title}
                style={{
                  background: "var(--color-canvas)",
                  padding: "32px",
                  animation: `fade-up 0.6s cubic-bezier(0.16,1,0.3,1) ${300 + i * 80}ms both`,
                }}
              >
                <div style={{
                  width: "36px", height: "36px",
                  background: "var(--color-canvas-soft-2)",
                  borderRadius: "8px",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  marginBottom: "16px",
                }}>
                  <Icon size={18} color="var(--color-ink)" weight="duotone" />
                </div>
                <h3 style={{
                  fontSize: "15px", fontWeight: 600,
                  color: "var(--color-ink)", marginBottom: "8px",
                  letterSpacing: "-0.01em",
                }}>
                  {feat.title}
                </h3>
                <p style={{ fontSize: "14px", color: "var(--color-body)", lineHeight: 1.6 }}>
                  {feat.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
