"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Bot, FileText, Send, User as UserIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Markdown } from "@/components/markdown";
import { streamChat } from "@/hooks/use-chat";
import { useCourse } from "@/hooks/use-courses";
import { cn } from "@/lib/utils";
import type { Source } from "@/types";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

const SUGGESTIONS = [
  "Summarize this document",
  "Explain the key concepts",
  "Generate a quiz question",
  "What should I learn next?",
];

export default function ChatPage() {
  const params = useParams<{ courseId: string }>();
  const courseId = params.courseId;
  const { data: course } = useCourse(courseId);
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [input, setInput] = React.useState("");
  const [streaming, setStreaming] = React.useState(false);
  const [sessionId, setSessionId] = React.useState<string | null>(null);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || streaming) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: message }, { role: "assistant", content: "" }]);
    setStreaming(true);

    await streamChat(
      { course_id: courseId, session_id: sessionId, message },
      {
        onSession: (id) => setSessionId(id),
        onSources: (sources) =>
          setMessages((prev) => {
            const copy = [...prev];
            copy[copy.length - 1] = { ...copy[copy.length - 1], sources };
            return copy;
          }),
        onToken: (token) =>
          setMessages((prev) => {
            const copy = [...prev];
            copy[copy.length - 1] = {
              ...copy[copy.length - 1],
              content: copy[copy.length - 1].content + token,
            };
            return copy;
          }),
        onDone: () => setStreaming(false),
        onError: () => {
          setMessages((prev) => {
            const copy = [...prev];
            copy[copy.length - 1] = {
              ...copy[copy.length - 1],
              content:
                copy[copy.length - 1].content ||
                "Sorry, I couldn't generate a response. Please try again.",
            };
            return copy;
          });
          setStreaming(false);
        },
      }
    );
  };

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-3xl flex-col">
      <div className="mb-4 flex items-center gap-2">
        <Link href={`/courses/${courseId}`} className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> Back
        </Link>
        <div className="ml-2">
          <h1 className="flex items-center gap-2 text-lg font-semibold">
            <Bot className="h-5 w-5 text-primary" /> AI Tutor
          </h1>
          <p className="text-xs text-muted-foreground">{course?.title}</p>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto rounded-xl border bg-card/40 p-4">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
            <div className="rounded-full bg-primary/10 p-4">
              <Bot className="h-8 w-8 text-primary" />
            </div>
            <div>
              <p className="font-medium">Ask anything about this document</p>
              <p className="text-sm text-muted-foreground">Answers come only from your uploaded PDF.</p>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-full border px-3 py-1.5 text-sm hover:bg-accent"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={cn("flex gap-3", msg.role === "user" && "flex-row-reverse")}>
              <div
                className={cn(
                  "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                  msg.role === "user" ? "bg-secondary" : "bg-primary/10"
                )}
              >
                {msg.role === "user" ? (
                  <UserIcon className="h-4 w-4" />
                ) : (
                  <Bot className="h-4 w-4 text-primary" />
                )}
              </div>
              <div
                className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-3",
                  msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-card border"
                )}
              >
                {msg.content ? (
                  msg.role === "assistant" ? (
                    <Markdown content={msg.content} />
                  ) : (
                    <p className="text-sm">{msg.content}</p>
                  )
                ) : (
                  <span className="inline-flex gap-1">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground" />
                  </span>
                )}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 space-y-1 border-t pt-2">
                    <p className="text-xs font-medium text-muted-foreground">Sources</p>
                    <div className="flex flex-wrap gap-1">
                      {msg.sources.map((src, si) => (
                        <Badge key={si} variant="outline" className="gap-1 text-xs">
                          <FileText className="h-3 w-3" />
                          {src.page_number ? `Page ${src.page_number}` : `Chunk ${src.chunk_index ?? si + 1}`}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <Card className="mt-4">
        <CardContent className="p-3">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            className="flex items-end gap-2"
          >
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
              placeholder="Ask a question about this document…"
              className="min-h-[44px] max-h-32 resize-none"
              rows={1}
            />
            <Button type="submit" size="icon" disabled={streaming || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
