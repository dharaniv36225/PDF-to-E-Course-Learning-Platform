"use client";

import Link from "next/link";
import { BookOpen } from "lucide-react";
import { CourseCard } from "@/components/course-card";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCourses } from "@/hooks/use-courses";

export default function CoursesPage() {
  const { data: courses, isLoading } = useCourses();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">My Courses</h1>
          <p className="text-muted-foreground">All courses generated from your PDFs.</p>
        </div>
        <Link href="/upload">
          <Button>New course</Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-48 w-full" />
          ))}
        </div>
      ) : courses && courses.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-16 text-center">
            <BookOpen className="h-10 w-10 text-muted-foreground" />
            <p className="text-muted-foreground">You don&apos;t have any courses yet.</p>
            <Link href="/upload">
              <Button>Upload a PDF</Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
