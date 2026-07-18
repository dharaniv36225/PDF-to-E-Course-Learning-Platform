"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { CheckCircle2, FileText, Loader2, Sparkles, Trash2, UploadCloud, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Spinner } from "@/components/ui/spinner";
import { useGenerateCourse } from "@/hooks/use-courses";
import { useDeleteUpload, useUploadPdfs, useUploads } from "@/hooks/use-uploads";
import { getApiErrorMessage } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Upload } from "@/types";

const statusBadge: Record<string, { variant: "default" | "success" | "warning" | "destructive"; label: string }> = {
  ready: { variant: "success", label: "Ready" },
  processing: { variant: "warning", label: "Processing" },
  uploaded: { variant: "default", label: "Uploaded" },
  failed: { variant: "destructive", label: "Failed" },
};

export default function UploadPage() {
  const router = useRouter();
  const { data: uploads, isLoading } = useUploads();
  const [progress, setProgress] = React.useState(0);
  const upload = useUploadPdfs(setProgress);
  const deleteUpload = useDeleteUpload();
  const generate = useGenerateCourse();
  const [dragOver, setDragOver] = React.useState(false);
  const [generatingId, setGeneratingId] = React.useState<string | null>(null);
  const inputRef = React.useRef<HTMLInputElement>(null);

  const handleFiles = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    const files = Array.from(fileList).filter((f) => f.type === "application/pdf" || f.name.endsWith(".pdf"));
    if (files.length === 0) {
      toast.error("Please select PDF files only");
      return;
    }
    setProgress(0);
    try {
      await upload.mutateAsync(files);
      toast.success(`${files.length} file(s) uploaded and processed`);
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    } finally {
      setProgress(0);
    }
  };

  const handleGenerate = async (uploadId: string) => {
    setGeneratingId(uploadId);
    try {
      const course = await generate.mutateAsync({ upload_id: uploadId });
      toast.success("Course generated!");
      router.push(`/courses/${course.id}`);
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    } finally {
      setGeneratingId(null);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Upload PDFs</h1>
        <p className="text-muted-foreground">Upload documents to turn them into AI courses.</p>
      </div>

      <motion.div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFiles(e.dataTransfer.files);
        }}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-12 text-center transition-colors",
          dragOver ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
        )}
        onClick={() => inputRef.current?.click()}
      >
        <div className="rounded-full bg-primary/10 p-4">
          <UploadCloud className="h-8 w-8 text-primary" />
        </div>
        <div>
          <p className="font-medium">Drag & drop PDFs here</p>
          <p className="text-sm text-muted-foreground">or click to browse — multiple files supported</p>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        {upload.isPending && (
          <div className="mt-4 w-full max-w-sm space-y-2">
            <Progress value={progress} />
            <p className="text-xs text-muted-foreground">Uploading & processing… {progress}%</p>
          </div>
        )}
      </motion.div>

      <div>
        <h2 className="mb-4 text-lg font-semibold">Your documents</h2>
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Card key={i}>
                <CardContent className="h-20" />
              </Card>
            ))}
          </div>
        ) : uploads && uploads.length > 0 ? (
          <div className="space-y-3">
            {uploads.map((item: Upload) => {
              const badge = statusBadge[item.status] ?? statusBadge.uploaded;
              return (
                <Card key={item.id}>
                  <CardHeader className="flex-row items-center justify-between gap-4 space-y-0 py-4">
                    <div className="flex min-w-0 items-center gap-3">
                      <div className="rounded-lg bg-primary/10 p-2">
                        <FileText className="h-5 w-5 text-primary" />
                      </div>
                      <div className="min-w-0">
                        <CardTitle className="truncate text-sm">{item.original_filename}</CardTitle>
                        <p className="text-xs text-muted-foreground">
                          {item.page_count} pages · {(item.size_bytes / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={badge.variant} className="gap-1">
                        {item.status === "ready" && <CheckCircle2 className="h-3 w-3" />}
                        {item.status === "processing" && <Loader2 className="h-3 w-3 animate-spin" />}
                        {item.status === "failed" && <XCircle className="h-3 w-3" />}
                        {badge.label}
                      </Badge>
                      <Button
                        size="sm"
                        variant="default"
                        className="gap-1"
                        disabled={item.status !== "ready" || generatingId === item.id}
                        onClick={() => handleGenerate(item.id)}
                      >
                        {generatingId === item.id ? (
                          <Spinner />
                        ) : (
                          <>
                            <Sparkles className="h-3.5 w-3.5" /> Generate course
                          </>
                        )}
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => deleteUpload.mutate(item.id)}
                        aria-label="Delete upload"
                      >
                        <Trash2 className="h-4 w-4 text-muted-foreground" />
                      </Button>
                    </div>
                  </CardHeader>
                </Card>
              );
            })}
          </div>
        ) : (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              No documents uploaded yet.
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
