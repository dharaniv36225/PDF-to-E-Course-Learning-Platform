"use client";

import { useQuery } from "@tanstack/react-query";
import { getData } from "@/lib/api";
import type { DashboardStats, SearchResponse } from "@/types";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: () => getData<DashboardStats>("/dashboard"),
  });
}

export function useSearch(query: string, courseId?: string) {
  return useQuery({
    queryKey: ["search", query, courseId ?? null],
    queryFn: () =>
      getData<SearchResponse>("/search", { params: { q: query, course_id: courseId } }),
    enabled: query.trim().length > 0,
  });
}
