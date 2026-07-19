"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteData, getData, postData } from "@/lib/api";
import type { CourseDetail, CourseWithProgress, Lesson } from "@/types";

export function useCourses() {
  return useQuery({
    queryKey: ["courses"],
    queryFn: () => getData<CourseWithProgress[]>("/courses"),
  });
}

export function useCourse(courseId: string) {
  return useQuery({
    queryKey: ["course", courseId],
    queryFn: () => getData<CourseDetail>(`/courses/${courseId}`),
    enabled: Boolean(courseId),
  });
}

export function useLesson(courseId: string, lessonId: string) {
  return useQuery({
    queryKey: ["lesson", courseId, lessonId],
    queryFn: () => getData<Lesson>(`/courses/${courseId}/lessons/${lessonId}`),
    enabled: Boolean(courseId && lessonId),
  });
}

export function useGenerateCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { upload_id: string; difficulty?: string; max_chapters?: number }) =>
      postData<CourseDetail>("/courses/generate", payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

export function useDeleteCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (courseId: string) => deleteData(`/courses/${courseId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}
