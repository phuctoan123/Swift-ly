"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiGetUrls, apiDeleteUrl } from "@/lib/api";

export function useUrls(limit = 20, offset = 0) {
  return useQuery({
    queryKey: ["urls", limit, offset],
    queryFn: () => apiGetUrls(limit, offset),
    staleTime: 30_000,
  });
}

export function useDeleteUrl() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: apiDeleteUrl,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["urls"] }),
  });
}
