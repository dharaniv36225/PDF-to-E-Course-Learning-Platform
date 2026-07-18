"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useUpdateLessonProgress(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      lessonId: string;
      completed?: boolean;
      time_spent_seconds?: number;
      last_position?: number;
    }) => {
      const { lessonId, ...body } = payload;
      const { data } = await api.put(
        `/progress/courses/${courseId}/lessons/${lessonId}`,
        body
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["course-progress", courseId] });
    },
  });
}
