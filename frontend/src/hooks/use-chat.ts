"use client";

import { useQuery } from "@tanstack/react-query";
import { API_URL, api, tokenStore } from "@/lib/api";
import type { ChatSession, Source } from "@/types";

export function useChatSessions(courseId: string) {
  return useQuery({
    queryKey: ["chat-sessions", courseId],
    queryFn: async () => {
      const { data } = await api.get<ChatSession[]>("/chat/sessions", {
        params: { course_id: courseId },
      });
      return data;
    },
    enabled: Boolean(courseId),
  });
}

export function useChatSession(sessionId: string | null) {
  return useQuery({
    queryKey: ["chat-session", sessionId],
    queryFn: async () => {
      const { data } = await api.get<ChatSession>(`/chat/sessions/${sessionId}`);
      return data;
    },
    enabled: Boolean(sessionId),
  });
}

export interface StreamCallbacks {
  onSession?: (sessionId: string) => void;
  onSources?: (sources: Source[]) => void;
  onToken?: (token: string) => void;
  onDone?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Streams a chat answer using Server-Sent Events from the backend /chat/stream endpoint.
 */
export async function streamChat(
  payload: { course_id: string; session_id?: string | null; message: string },
  callbacks: StreamCallbacks
): Promise<void> {
  const token = tokenStore.get();
  try {
    const response = await fetch(`${API_URL}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ ...payload, stream: true }),
    });

    if (!response.ok || !response.body) {
      throw new Error(`Chat request failed with status ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() ?? "";
      for (const chunk of events) {
        const line = chunk.trim();
        if (!line.startsWith("data:")) continue;
        const json = line.slice(5).trim();
        if (!json) continue;
        const event = JSON.parse(json) as {
          type: string;
          session_id?: string;
          sources?: Source[];
          content?: string;
        };
        if (event.type === "session" && event.session_id) callbacks.onSession?.(event.session_id);
        else if (event.type === "sources") callbacks.onSources?.(event.sources ?? []);
        else if (event.type === "token") callbacks.onToken?.(event.content ?? "");
        else if (event.type === "done") callbacks.onDone?.();
      }
    }
    callbacks.onDone?.();
  } catch (error) {
    callbacks.onError?.(error instanceof Error ? error : new Error("Stream failed"));
  }
}
