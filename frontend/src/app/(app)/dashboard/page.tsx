"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { BookOpen, Clock, Flame, Trophy, Upload as UploadIcon } from "lucide-react";
import { ActivityChart, QuizScoreChart } from "@/components/charts";
import { CourseCard } from "@/components/course-card";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useDashboard } from "@/hooks/use-dashboard";
import { useAuthStore } from "@/store/auth-store";
import { formatMinutes } from "@/lib/utils";

export default function DashboardPage() {
  const { data, isLoading } = useDashboard();
  const user = useAuthStore((s) => s.user);

  const stats = [
    { label: "Courses", value: data?.total_courses ?? 0, icon: BookOpen },
    { label: "Uploads", value: data?.total_uploads ?? 0, icon: UploadIcon },
    { label: "Avg quiz score", value: `${data?.average_quiz_score ?? 0}%`, icon: Trophy },
    { label: "Learning streak", value: `${data?.learning_streak_days ?? 0}d`, icon: Flame },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">
            Welcome back{user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""} 👋
          </h1>
          <p className="text-muted-foreground">Here&apos;s your learning overview.</p>
        </div>
        <Link href="/upload">
          <Button className="gap-2">
            <UploadIcon className="h-4 w-4" /> Upload PDF
          </Button>
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Card>
                <CardContent className="flex items-center gap-4 pt-6">
                  <div className="rounded-lg bg-primary/10 p-3">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    {isLoading ? (
                      <Skeleton className="h-7 w-16" />
                    ) : (
                      <p className="text-2xl font-bold">{stat.value}</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle className="text-base">Learning activity (14 days)</CardTitle>
            <span className="flex items-center gap-1 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" /> {formatMinutes(data?.total_time_spent_minutes ?? 0)}
            </span>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[240px] w-full" />
            ) : (
              <ActivityChart data={data?.activity ?? []} />
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent quiz scores</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[240px] w-full" />
            ) : data && data.quiz_scores.length > 0 ? (
              <QuizScoreChart data={[...data.quiz_scores].reverse()} />
            ) : (
              <div className="flex h-[240px] items-center justify-center text-sm text-muted-foreground">
                No quiz attempts yet
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Recent courses</h2>
          <Link href="/courses" className="text-sm text-primary hover:underline">
            View all
          </Link>
        </div>
        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-48 w-full" />
            ))}
          </div>
        ) : data && data.recent_courses.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.recent_courses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
              <BookOpen className="h-10 w-10 text-muted-foreground" />
              <p className="text-muted-foreground">No courses yet. Upload a PDF to get started.</p>
              <Link href="/upload">
                <Button>Upload your first PDF</Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
