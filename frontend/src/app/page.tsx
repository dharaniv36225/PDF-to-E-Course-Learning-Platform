"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  BookOpen,
  Bot,
  FileText,
  GraduationCap,
  ListChecks,
  Sparkles,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ThemeToggle } from "@/components/theme-toggle";

const FEATURES = [
  { icon: FileText, title: "Smart PDF Extraction", desc: "PyMuPDF parses and chunks any PDF, preserving page-level citations." },
  { icon: Sparkles, title: "AI Course Generation", desc: "Auto-build chapters, lessons, summaries and key takeaways in seconds." },
  { icon: Bot, title: "RAG Chatbot", desc: "Ask questions answered strictly from your document, with streaming and sources." },
  { icon: ListChecks, title: "Auto Quizzes", desc: "MCQs, true/false and short-answer questions with instant grading." },
  { icon: BookOpen, title: "Progress Tracking", desc: "Mark lessons complete, resume later and track your completion %." },
  { icon: Zap, title: "Semantic Search", desc: "Find concepts across lessons and documents with vector search." },
];

const STEPS = [
  { step: "1", title: "Upload", desc: "Drag & drop one or more PDFs." },
  { step: "2", title: "Generate", desc: "AI builds your structured course." },
  { step: "3", title: "Learn", desc: "Study, chat, quiz and track progress." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-primary/5">
      <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-6 w-6 text-primary" />
            <span className="text-lg font-bold gradient-text">LearnPDF</span>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Link href="/login">
              <Button variant="ghost">Sign in</Button>
            </Link>
            <Link href="/register">
              <Button>Get started</Button>
            </Link>
          </div>
        </div>
      </header>

      <section className="container py-24 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border bg-card px-4 py-1.5 text-sm">
            <Sparkles className="h-4 w-4 text-primary" />
            Powered by RAG, Groq & Sentence Transformers
          </div>
          <h1 className="mx-auto max-w-4xl text-4xl font-extrabold tracking-tight sm:text-6xl">
            Turn any PDF into an <span className="gradient-text">AI-powered course</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            Upload a document and instantly get structured chapters, lessons, quizzes and a
            chatbot that answers questions using only your content.
          </p>
          <div className="mt-8 flex items-center justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="gap-2">
                Start learning free <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline">
                I already have an account
              </Button>
            </Link>
          </div>
        </motion.div>
      </section>

      <section className="container pb-24">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.05 }}
              >
                <Card className="h-full transition-shadow hover:shadow-lg">
                  <CardContent className="pt-6">
                    <div className="mb-4 inline-flex rounded-lg bg-primary/10 p-3">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <h3 className="mb-2 font-semibold">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground">{feature.desc}</p>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </section>

      <section className="container pb-24">
        <h2 className="mb-12 text-center text-3xl font-bold">How it works</h2>
        <div className="grid gap-8 md:grid-cols-3">
          {STEPS.map((s) => (
            <div key={s.step} className="text-center">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-2xl font-bold text-primary-foreground">
                {s.step}
              </div>
              <h3 className="mb-1 text-xl font-semibold">{s.title}</h3>
              <p className="text-muted-foreground">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="container pb-24">
        <Card className="overflow-hidden bg-gradient-to-r from-primary/10 via-fuchsia-500/10 to-indigo-500/10">
          <CardContent className="flex flex-col items-center gap-4 py-16 text-center">
            <h2 className="text-3xl font-bold">Ready to learn smarter?</h2>
            <p className="max-w-xl text-muted-foreground">
              Join learners turning dense documents into interactive courses.
            </p>
            <Link href="/register">
              <Button size="lg" className="gap-2">
                Create your free account <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      </section>

      <footer className="border-t py-8">
        <div className="container flex flex-col items-center justify-between gap-4 text-sm text-muted-foreground sm:flex-row">
          <p>&copy; {new Date().getFullYear()} LearnPDF. Built with Next.js & FastAPI.</p>
          <div className="flex gap-4">
            <Link href="/login" className="hover:text-foreground">Sign in</Link>
            <Link href="/register" className="hover:text-foreground">Register</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
