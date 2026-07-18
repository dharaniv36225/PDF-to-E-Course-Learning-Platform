"use client";

import * as React from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Lightbulb,
  ListChecks,
  MessageSquare,
  ScrollText,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { Markdown } from "@/components/markdown";
import { useCourse } from "@/hooks/use-courses";
import { useUpdateLessonProgress } from "@/hooks/use-progress";
import { formatMinutes } from "@/lib/utils";
import type { Lesson } from "@/types";

export default function LessonPage() {
  const params = useParams<{ courseId: string; lessonId: string }>();
  const { courseId, lessonId } = params;
  const router = useRouter();
  const { data: course, isLoading } = useCourse(courseId);
  const updateProgress = useUpdateLessonProgress(courseId);
  const startRef = React.useRef<number>(Date.now());

  React.useEffect(() => {
    startRef.current = Date.now();
  }, [lessonId]);

  const flat = React.useMemo<Lesson[]>(() => {
    if (!course) return [];
    return course.chapters.flatMap((c) => c.lessons);
  }, [course]);

  const index = flat.findIndex((l) => l.id === lessonId);
  const lesson = flat[index];
  const prev = index > 0 ? flat[index - 1] : null;
  const next = index >= 0 && index < flat.length - 1 ? flat[index + 1] : null;

  const markComplete = async (goNext: boolean) => {
    const seconds = Math.round((Date.now() - startRef.current) / 1000);
    try {
      await updateProgress.mutateAsync({
        lessonId,
        completed: true,
        time_spent_seconds: seconds,
      });
      toast.success("Lesson marked complete");
      if (goNext && next) {
        router.push(`/courses/${courseId}/lessons/${next.id}`);
      }
    } catch {
      toast.error("Could not update progress");
    }
  };

  if (isLoading || !course) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="mx-auto max-w-3xl text-center">
        <p className="text-muted-foreground">Lesson not found.</p>
        <Link href={`/courses/${courseId}`}>
          <Button variant="outline" className="mt-4">Back to course</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <Link href={`/courses/${courseId}`} className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> {course.title}
        </Link>
        <span className="text-xs text-muted-foreground">
          Lesson {index + 1} of {flat.length}
        </span>
      </div>

      <div className="space-y-2">
        <Badge variant="secondary">{formatMinutes(lesson.estimated_minutes)}</Badge>
        <h1 className="text-3xl font-bold">{lesson.title}</h1>
      </div>

      {lesson.explanation && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <BookOpen className="h-4 w-4 text-primary" /> Explanation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Markdown content={lesson.explanation} />
          </CardContent>
        </Card>
      )}

      {lesson.content && !lesson.explanation && (
        <Card>
          <CardContent className="pt-6">
            <Markdown content={lesson.content} />
          </CardContent>
        </Card>
      )}

      {lesson.examples && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Lightbulb className="h-4 w-4 text-amber-500" /> Examples
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Markdown content={lesson.examples} />
          </CardContent>
        </Card>
      )}

      {lesson.important_notes && (
        <Card className="border-amber-500/40 bg-amber-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <ScrollText className="h-4 w-4 text-amber-600" /> Important notes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Markdown content={lesson.important_notes} />
          </CardContent>
        </Card>
      )}

      {lesson.summary && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <Markdown content={lesson.summary} />
          </CardContent>
        </Card>
      )}

      {lesson.key_takeaways && lesson.key_takeaways.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <ListChecks className="h-4 w-4 text-primary" /> Key takeaways
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {lesson.key_takeaways.map((item, i) => (
                <li key={i} className="flex gap-2">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                  {item}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3 border-t pt-6">
        <div className="flex gap-2">
          {prev && (
            <Link href={`/courses/${courseId}/lessons/${prev.id}`}>
              <Button variant="outline" className="gap-1">
                <ArrowLeft className="h-4 w-4" /> Previous
              </Button>
            </Link>
          )}
          <Link href={`/courses/${courseId}/chat`}>
            <Button variant="ghost" className="gap-1">
              <MessageSquare className="h-4 w-4" /> Ask AI
            </Button>
          </Link>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => markComplete(false)} disabled={updateProgress.isPending}>
            {updateProgress.isPending ? <Spinner /> : "Mark complete"}
          </Button>
          {next ? (
            <Button className="gap-1" onClick={() => markComplete(true)} disabled={updateProgress.isPending}>
              Complete & next <ArrowRight className="h-4 w-4" />
            </Button>
          ) : (
            <Button className="gap-1" onClick={() => markComplete(false)} disabled={updateProgress.isPending}>
              Finish course <CheckCircle2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
