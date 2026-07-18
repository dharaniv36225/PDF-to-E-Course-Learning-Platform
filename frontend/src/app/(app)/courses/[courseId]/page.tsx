"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  BookOpen,
  CheckCircle2,
  ChevronDown,
  Clock,
  ListChecks,
  MessageSquare,
  Target,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCourse } from "@/hooks/use-courses";
import { cn, formatMinutes } from "@/lib/utils";

export default function CourseDetailPage() {
  const params = useParams<{ courseId: string }>();
  const courseId = params.courseId;
  const { data: course, isLoading } = useCourse(courseId);
  const [openChapter, setOpenChapter] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (course && course.chapters.length > 0) {
      setOpenChapter(course.chapters[0].id);
    }
  }, [course]);

  if (isLoading || !course) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  const totalLessons = course.chapters.reduce((sum, c) => sum + c.lessons.length, 0);

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <Card className="overflow-hidden">
        <div className="h-2 bg-gradient-to-r from-primary via-fuchsia-500 to-indigo-500" />
        <CardContent className="space-y-4 pt-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-2">
              <div className="flex flex-wrap gap-2">
                <Badge>{course.difficulty}</Badge>
                <Badge variant="secondary" className="gap-1">
                  <Clock className="h-3 w-3" /> {formatMinutes(course.estimated_minutes)}
                </Badge>
                <Badge variant="secondary" className="gap-1">
                  <BookOpen className="h-3 w-3" /> {totalLessons} lessons
                </Badge>
              </div>
              <h1 className="text-3xl font-bold">{course.title}</h1>
              <p className="max-w-2xl text-muted-foreground">{course.description}</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href={`/courses/${courseId}/chat`}>
              <Button variant="outline" className="gap-2">
                <MessageSquare className="h-4 w-4" /> Ask AI tutor
              </Button>
            </Link>
            <Link href={`/courses/${courseId}/quiz`}>
              <Button variant="outline" className="gap-2">
                <ListChecks className="h-4 w-4" /> Quizzes
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-3">
        {course.learning_objectives && course.learning_objectives.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Target className="h-4 w-4 text-primary" /> Learning objectives
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                {course.learning_objectives.map((obj, i) => (
                  <li key={i} className="flex gap-2">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                    {obj}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
        {course.prerequisites && course.prerequisites.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Prerequisites</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                {course.prerequisites.map((p, i) => (
                  <li key={i}>• {p}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
        {course.tags && course.tags.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Topics</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {course.tags.map((tag) => (
                <Badge key={tag} variant="outline">
                  {tag}
                </Badge>
              ))}
            </CardContent>
          </Card>
        )}
      </div>

      <div className="space-y-3">
        <h2 className="text-xl font-semibold">Course content</h2>
        {course.chapters.map((chapter, index) => {
          const open = openChapter === chapter.id;
          return (
            <Card key={chapter.id}>
              <button
                className="flex w-full items-center justify-between p-4 text-left"
                onClick={() => setOpenChapter(open ? null : chapter.id)}
              >
                <div>
                  <p className="text-xs text-muted-foreground">Chapter {index + 1}</p>
                  <p className="font-semibold">{chapter.title}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">{chapter.lessons.length} lessons</span>
                  <ChevronDown className={cn("h-5 w-5 transition-transform", open && "rotate-180")} />
                </div>
              </button>
              {open && (
                <div className="border-t">
                  {chapter.summary && (
                    <p className="px-4 py-3 text-sm text-muted-foreground">{chapter.summary}</p>
                  )}
                  <ul className="divide-y">
                    {chapter.lessons.map((lesson, li) => (
                      <li key={lesson.id}>
                        <Link
                          href={`/courses/${courseId}/lessons/${lesson.id}`}
                          className="flex items-center justify-between px-4 py-3 text-sm hover:bg-accent"
                        >
                          <span className="flex items-center gap-3">
                            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs text-primary">
                              {li + 1}
                            </span>
                            {lesson.title}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {formatMinutes(lesson.estimated_minutes)}
                          </span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {course.chapters[0]?.lessons[0] && (
        <div className="flex justify-center">
          <Link href={`/courses/${courseId}/lessons/${course.chapters[0].lessons[0].id}`}>
            <Button size="lg" className="gap-2">
              <BookOpen className="h-4 w-4" /> Start learning
            </Button>
          </Link>
        </div>
      )}
    </div>
  );
}
