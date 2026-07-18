"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Quiz, QuizAttemptResult } from "@/types";

export function useCourseQuizzes(courseId: string) {
  return useQuery({
    queryKey: ["quizzes", courseId],
    queryFn: async () => {
      const { data } = await api.get<Quiz[]>(`/quizzes/course/${courseId}`);
      return data;
    },
    enabled: Boolean(courseId),
  });
}

export function useQuiz(quizId: string | null) {
  return useQuery({
    queryKey: ["quiz", quizId],
    queryFn: async () => {
      const { data } = await api.get<Quiz>(`/quizzes/${quizId}`);
      return data;
    },
    enabled: Boolean(quizId),
  });
}

export function useGenerateQuiz() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      course_id: string;
      chapter_id?: string;
      num_questions: number;
      question_types: string[];
    }) => {
      const { data } = await api.post<Quiz>("/quizzes/generate", payload);
      return data;
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["quizzes", variables.course_id] });
    },
  });
}

export function useSubmitQuiz() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      quizId: string;
      answers: { question_id: string; answer: string }[];
    }) => {
      const { data } = await api.post<QuizAttemptResult>(`/quizzes/${payload.quizId}/submit`, {
        answers: payload.answers,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
