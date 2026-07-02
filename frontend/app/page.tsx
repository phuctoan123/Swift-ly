import type { Metadata } from "next";
import { HeroSection } from "@/components/landing/hero-section";

export const metadata: Metadata = {
  title: "Short.ly — Rút gọn URL, theo dõi analytics",
  description: "Dịch vụ rút gọn URL production-ready với Redis cache, JWT auth và analytics thời gian thực.",
};

export default function LandingPage() {
  return <HeroSection />;
}
