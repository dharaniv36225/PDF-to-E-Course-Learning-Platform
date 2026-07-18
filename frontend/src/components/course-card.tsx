"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { BookOpen, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { formatMinutes } from "@/lib/utils";
import type { CourseWithProgress } from "@/types";

const difficultyVariant: Record<string, "default" | "success" | "warning" | "destructive"> = {
  beginner: "success",
  intermediate: "warning",
  advanced: "destructive",
};

export function CourseCard({ course }: { course: CourseWithProgress }) {
  return (
    <motion.div whileHover={{ y: -4 }} transition={{ duration: 0.2 }}>
      <Link href={`/courses/${course.id}`}>
        <Card className="h-full transition-shadow hover:shadow-lg">
          <CardHeader>
            <div className="flex items-start justify-between gap-2">
              <CardTitle className="line-clamp-2 text-base">{course.title}</CardTitle>
              <Badge variant={difficultyVariant[course.difficulty] ?? "default"}>
                {course.difficulty}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="line-clamp-2 text-sm text-muted-foreground">
              {course.description ?? "No description"}
            </p>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <BookOpen className="h-3.5 w-3.5" /> {course.total_lessons} lessons
              </span>
              <span className="flex items-center gap-1">
                <Clock className="h-3.5 w-3.5" /> {formatMinutes(course.estimated_minutes)}
              </span>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-medium">{course.completion_percent}%</span>
              </div>
              <Progress value={course.completion_percent} />
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}
