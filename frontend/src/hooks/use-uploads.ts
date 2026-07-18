"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Upload } from "@/types";

export function useUploads() {
  return useQuery({
    queryKey: ["uploads"],
    queryFn: async () => {
      const { data } = await api.get<Upload[]>("/uploads");
      return data;
    },
  });
}

export function useUploadPdfs(onProgress?: (percent: number) => void) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (files: File[]) => {
      const form = new FormData();
      files.forEach((file) => form.append("files", file));
      const { data } = await api.post<Upload[]>("/uploads", form, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => {
          if (event.total) {
            onProgress?.(Math.round((event.loaded / event.total) * 100));
          }
        },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["uploads"] });
    },
  });
}

export function useDeleteUpload() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (uploadId: string) => {
      await api.delete(`/uploads/${uploadId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["uploads"] });
    },
  });
}
