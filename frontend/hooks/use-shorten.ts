"use client";

import { useMutation } from "@tanstack/react-query";
import { apiShorten } from "@/lib/api";
import type { ShortenRequest, ShortenResponse, APIError } from "@/types";

export function useShorten() {
  return useMutation<ShortenResponse, Error & { status?: number; data?: APIError }, ShortenRequest>({
    mutationFn: apiShorten,
  });
}
