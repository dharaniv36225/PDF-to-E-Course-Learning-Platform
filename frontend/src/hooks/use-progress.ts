"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { putData } from "@/lib/api";

export function useUpdateLessonProgress(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: {
      lessonId: string;
      completed?: boolean;
      time_spent_seconds?: number;
      last_position?: number;
    }) => {
      const { lessonId, ...body } = payload;
      return putData(`/progress/courses/${courseId}/lessons/${lessonId}`, body);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["course-progress", courseId] });
    },
  });
}
