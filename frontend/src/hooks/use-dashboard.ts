"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { DashboardStats, SearchResponse } from "@/types";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const { data } = await api.get<DashboardStats>("/dashboard");
      return data;
    },
  });
}

export function useSearch(query: string, courseId?: string) {
  return useQuery({
    queryKey: ["search", query, courseId ?? null],
    queryFn: async () => {
      const { data } = await api.get<SearchResponse>("/search", {
        params: { q: query, course_id: courseId },
      });
      return data;
    },
    enabled: query.trim().length > 0,
  });
}
