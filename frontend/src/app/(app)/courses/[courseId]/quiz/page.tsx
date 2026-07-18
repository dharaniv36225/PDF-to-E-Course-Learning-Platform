"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import { ArrowLeft, CheckCircle2, ListChecks, Sparkles, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { useCourseQuizzes, useGenerateQuiz, useQuiz, useSubmitQuiz } from "@/hooks/use-quiz";
import { getApiErrorMessage } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { QuizAttemptResult } from "@/types";

const QUESTION_TYPES = [
  { id: "mcq", label: "Multiple choice" },
  { id: "true_false", label: "True / False" },
  { id: "short_answer", label: "Short answer" },
];

export default function QuizPage() {
  const params = useParams<{ courseId: string }>();
  const courseId = params.courseId;
  const { data: quizzes, isLoading } = useCourseQuizzes(courseId);
  const generate = useGenerateQuiz();
  const submit = useSubmitQuiz();

  const [activeQuizId, setActiveQuizId] = React.useState<string | null>(null);
  const { data: activeQuiz } = useQuiz(activeQuizId);
  const [answers, setAnswers] = React.useState<Record<string, string>>({});
  const [result, setResult] = React.useState<QuizAttemptResult | null>(null);

  const [numQuestions, setNumQuestions] = React.useState(5);
  const [selectedTypes, setSelectedTypes] = React.useState<string[]>(["mcq", "true_false"]);

  const toggleType = (id: string) => {
    setSelectedTypes((prev) => (prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]));
  };

  const onGenerate = async () => {
    if (selectedTypes.length === 0) {
      toast.error("Select at least one question type");
      return;
    }
    try {
      const quiz = await generate.mutateAsync({
        course_id: courseId,
        num_questions: numQuestions,
        question_types: selectedTypes,
      });
      toast.success("Quiz generated!");
      startQuiz(quiz.id);
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    }
  };

  const startQuiz = (quizId: string) => {
    setActiveQuizId(quizId);
    setAnswers({});
    setResult(null);
  };

  const onSubmit = async () => {
    if (!activeQuiz?.questions) return;
    const payload = activeQuiz.questions.map((q) => ({
      question_id: q.id,
      answer: answers[q.id] ?? "",
    }));
    try {
      const res = await submit.mutateAsync({ quizId: activeQuiz.id, answers: payload });
      setResult(res);
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    }
  };

  // Result view
  if (result && activeQuiz) {
    const passed = result.score >= 60;
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-8 text-center">
            <div className={cn("rounded-full p-4", passed ? "bg-emerald-500/10" : "bg-amber-500/10")}>
              <ListChecks className={cn("h-8 w-8", passed ? "text-emerald-500" : "text-amber-500")} />
            </div>
            <h2 className="text-3xl font-bold">{result.score}%</h2>
            <p className="text-muted-foreground">
              {result.correct_count} of {result.total_questions} correct
            </p>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => startQuiz(activeQuiz.id)}>
                Retry
              </Button>
              <Button
                onClick={() => {
                  setActiveQuizId(null);
                  setResult(null);
                }}
              >
                Back to quizzes
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {result.graded.map((g, i) => (
            <Card key={g.question_id} className={cn(g.is_correct ? "border-emerald-500/40" : "border-destructive/40")}>
              <CardHeader>
                <CardTitle className="flex items-start gap-2 text-base">
                  {g.is_correct ? (
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-500" />
                  ) : (
                    <XCircle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />
                  )}
                  <span>
                    {i + 1}. {g.question}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-1 text-sm">
                <p>
                  <span className="text-muted-foreground">Your answer: </span>
                  {g.submitted_answer || <em className="text-muted-foreground">blank</em>}
                </p>
                {!g.is_correct && (
                  <p>
                    <span className="text-muted-foreground">Correct answer: </span>
                    <span className="font-medium text-emerald-600 dark:text-emerald-400">{g.correct_answer}</span>
                  </p>
                )}
                {g.explanation && (
                  <p className="rounded-md bg-muted p-2 text-muted-foreground">{g.explanation}</p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  // Taking quiz view
  if (activeQuizId && activeQuiz?.questions) {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <button
          onClick={() => setActiveQuizId(null)}
          className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" /> Back to quizzes
        </button>
        <h1 className="text-2xl font-bold">{activeQuiz.title}</h1>
        <div className="space-y-4">
          {activeQuiz.questions.map((q, i) => (
            <Card key={q.id}>
              <CardHeader>
                <CardTitle className="text-base">
                  {i + 1}. {q.question}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {q.question_type === "mcq" && q.options ? (
                  <div className="space-y-2">
                    {q.options.map((opt) => (
                      <label
                        key={opt}
                        className={cn(
                          "flex cursor-pointer items-center gap-3 rounded-lg border p-3 text-sm transition-colors",
                          answers[q.id] === opt ? "border-primary bg-primary/5" : "hover:bg-accent"
                        )}
                      >
                        <input
                          type="radio"
                          name={q.id}
                          value={opt}
                          checked={answers[q.id] === opt}
                          onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: opt }))}
                          className="accent-[hsl(var(--primary))]"
                        />
                        {opt}
                      </label>
                    ))}
                  </div>
                ) : q.question_type === "true_false" ? (
                  <div className="flex gap-3">
                    {["True", "False"].map((opt) => (
                      <label
                        key={opt}
                        className={cn(
                          "flex flex-1 cursor-pointer items-center justify-center gap-2 rounded-lg border p-3 text-sm transition-colors",
                          answers[q.id] === opt ? "border-primary bg-primary/5" : "hover:bg-accent"
                        )}
                      >
                        <input
                          type="radio"
                          name={q.id}
                          value={opt}
                          checked={answers[q.id] === opt}
                          onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: opt }))}
                          className="hidden"
                        />
                        {opt}
                      </label>
                    ))}
                  </div>
                ) : (
                  <Input
                    placeholder="Type your answer…"
                    value={answers[q.id] ?? ""}
                    onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
                  />
                )}
              </CardContent>
            </Card>
          ))}
        </div>
        <Button className="w-full" onClick={onSubmit} disabled={submit.isPending}>
          {submit.isPending ? <Spinner /> : "Submit quiz"}
        </Button>
      </div>
    );
  }

  // List / generate view
  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div className="flex items-center gap-2">
        <Link href={`/courses/${courseId}`} className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> Back
        </Link>
        <h1 className="ml-2 text-2xl font-bold">Quizzes</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Sparkles className="h-4 w-4 text-primary" /> Generate a new quiz
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="num">Number of questions</Label>
              <Input
                id="num"
                type="number"
                min={1}
                max={20}
                value={numQuestions}
                onChange={(e) => setNumQuestions(Number(e.target.value))}
              />
            </div>
            <div className="space-y-2">
              <Label>Question types</Label>
              <div className="flex flex-wrap gap-2">
                {QUESTION_TYPES.map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => toggleType(t.id)}
                    className={cn(
                      "rounded-full border px-3 py-1.5 text-sm transition-colors",
                      selectedTypes.includes(t.id) ? "border-primary bg-primary/10 text-primary" : "hover:bg-accent"
                    )}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <Button onClick={onGenerate} disabled={generate.isPending} className="gap-2">
            {generate.isPending ? <Spinner /> : <Sparkles className="h-4 w-4" />}
            Generate quiz
          </Button>
        </CardContent>
      </Card>

      <div>
        <h2 className="mb-4 text-lg font-semibold">Available quizzes</h2>
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 2 }).map((_, i) => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </div>
        ) : quizzes && quizzes.length > 0 ? (
          <div className="space-y-3">
            {quizzes.map((quiz) => (
              <Card key={quiz.id}>
                <CardHeader className="flex-row items-center justify-between space-y-0 py-4">
                  <div>
                    <CardTitle className="text-base">{quiz.title}</CardTitle>
                    <Badge variant="secondary" className="mt-1">
                      {quiz.difficulty}
                    </Badge>
                  </div>
                  <Button onClick={() => startQuiz(quiz.id)}>Start</Button>
                </CardHeader>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              No quizzes yet. Generate one above.
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
