"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGetAnalytics } from "@/lib/api";

export function useAnalytics(shortCode: string) {
  return useQuery({
    queryKey: ["analytics", shortCode],
    queryFn: () => apiGetAnalytics(shortCode),
    enabled: !!shortCode,
    staleTime: 60_000,
  });
}
