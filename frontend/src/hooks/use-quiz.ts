"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getData, postData } from "@/lib/api";
import type { Quiz, QuizAttemptResult } from "@/types";

export function useCourseQuizzes(courseId: string) {
  return useQuery({
    queryKey: ["quizzes", courseId],
    queryFn: () => getData<Quiz[]>(`/quizzes/course/${courseId}`),
    enabled: Boolean(courseId),
  });
}

export function useQuiz(quizId: string | null) {
  return useQuery({
    queryKey: ["quiz", quizId],
    queryFn: () => getData<Quiz>(`/quizzes/${quizId}`),
    enabled: Boolean(quizId),
  });
}

export function useGenerateQuiz() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: {
      course_id: string;
      chapter_id?: string;
      num_questions: number;
      question_types: string[];
    }) => postData<Quiz>("/quizzes/generate", payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["quizzes", variables.course_id] });
    },
  });
}

export function useSubmitQuiz() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: {
      quizId: string;
      answers: { question_id: string; answer: string }[];
    }) =>
      postData<QuizAttemptResult>(`/quizzes/${payload.quizId}/submit`, {
        answers: payload.answers,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
