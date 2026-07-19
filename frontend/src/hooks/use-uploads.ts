"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteData, getData, postData } from "@/lib/api";
import type { Upload } from "@/types";

export function useUploads() {
  return useQuery({
    queryKey: ["uploads"],
    queryFn: () => getData<Upload[]>("/uploads"),
  });
}

export function useUploadPdfs(onProgress?: (percent: number) => void) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (files: File[]) => {
      const form = new FormData();
      files.forEach((file) => form.append("files", file));
      return postData<Upload[]>("/uploads", form, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => {
          if (event.total) {
            onProgress?.(Math.round((event.loaded / event.total) * 100));
          }
        },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["uploads"] });
    },
  });
}

export function useDeleteUpload() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (uploadId: string) => deleteData(`/uploads/${uploadId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["uploads"] });
    },
  });
}
