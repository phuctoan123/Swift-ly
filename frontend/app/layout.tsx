import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/components/providers";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";

export const metadata: Metadata = {
  title: { default: "Short.ly — URL Shortener", template: "%s | Short.ly" },
  description: "Rút gọn URL nhanh chóng. Theo dõi analytics. Quản lý liên kết của bạn.",
  keywords: ["url shortener", "rút gọn link", "analytics", "short.ly"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <QueryProvider>
          <Navbar />
          <main style={{ minHeight: "calc(100vh - 64px)" }}>{children}</main>
          <Footer />
        </QueryProvider>
      </body>
    </html>
  );
}
