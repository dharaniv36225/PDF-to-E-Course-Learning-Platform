"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { CourseDetail, CourseWithProgress, Lesson } from "@/types";

export function useCourses() {
  return useQuery({
    queryKey: ["courses"],
    queryFn: async () => {
      const { data } = await api.get<CourseWithProgress[]>("/courses");
      return data;
    },
  });
}

export function useCourse(courseId: string) {
  return useQuery({
    queryKey: ["course", courseId],
    queryFn: async () => {
      const { data } = await api.get<CourseDetail>(`/courses/${courseId}`);
      return data;
    },
    enabled: Boolean(courseId),
  });
}

export function useLesson(courseId: string, lessonId: string) {
  return useQuery({
    queryKey: ["lesson", courseId, lessonId],
    queryFn: async () => {
      const { data } = await api.get<Lesson>(`/courses/${courseId}/lessons/${lessonId}`);
      return data;
    },
    enabled: Boolean(courseId && lessonId),
  });
}

export function useGenerateCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { upload_id: string; difficulty?: string; max_chapters?: number }) => {
      const { data } = await api.post<CourseDetail>("/courses/generate", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

export function useDeleteCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (courseId: string) => {
      await api.delete(`/courses/${courseId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}
