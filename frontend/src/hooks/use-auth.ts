"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, getApiErrorMessage, tokenStore } from "@/lib/api";
import { getSupabase } from "@/lib/supabase";
import { useAuthStore } from "@/store/auth-store";
import type { AuthTokens, User } from "@/types";

async function fetchMe(): Promise<User> {
  const { data } = await api.get<User>("/auth/me");
  return data;
}

export function useCurrentUser() {
  const setUser = useAuthStore((s) => s.setUser);
  const setInitialized = useAuthStore((s) => s.setInitialized);

  const query = useQuery({
    queryKey: ["me"],
    queryFn: fetchMe,
    enabled: typeof window !== "undefined" && Boolean(tokenStore.get()),
    retry: false,
  });

  React.useEffect(() => {
    if (query.data) setUser(query.data);
    if (query.isError) setUser(null);
    if (!tokenStore.get()) setUser(null);
    if (query.isFetched || !tokenStore.get()) setInitialized(true);
  }, [query.data, query.isError, query.isFetched, setUser, setInitialized]);

  return query;
}

export function useLogin() {
  const router = useRouter();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { email: string; password: string }) => {
      const { data } = await api.post<AuthTokens>("/auth/login", payload);
      return data;
    },
    onSuccess: async (tokens) => {
      tokenStore.set(tokens.access_token, tokens.refresh_token);
      await queryClient.invalidateQueries({ queryKey: ["me"] });
      router.push("/dashboard");
    },
    onError: (error) => {
      throw new Error(getApiErrorMessage(error));
    },
  });
}

export function useRegister() {
  const router = useRouter();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { email: string; password: string; full_name?: string }) => {
      const { data } = await api.post<AuthTokens>("/auth/register", payload);
      return data;
    },
    onSuccess: async (tokens) => {
      tokenStore.set(tokens.access_token, tokens.refresh_token);
      await queryClient.invalidateQueries({ queryKey: ["me"] });
      router.push("/dashboard");
    },
    onError: (error) => {
      throw new Error(getApiErrorMessage(error));
    },
  });
}

export function useLogout() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const setUser = useAuthStore((s) => s.setUser);
  return React.useCallback(async () => {
    const supabase = getSupabase();
    if (supabase) await supabase.auth.signOut();
    tokenStore.clear();
    setUser(null);
    queryClient.clear();
    router.push("/login");
  }, [queryClient, router, setUser]);
}

export function useGoogleLogin() {
  return React.useCallback(async () => {
    const supabase = getSupabase();
    if (!supabase) {
      throw new Error("Supabase is not configured. Add NEXT_PUBLIC_SUPABASE_* env vars.");
    }
    const redirectTo = `${process.env.NEXT_PUBLIC_APP_URL ?? window.location.origin}/auth/callback`;
    await supabase.auth.signInWithOAuth({ provider: "google", options: { redirectTo } });
  }, []);
}

/** Exchange a Supabase session token for backend JWTs (used in OAuth callback). */
export async function exchangeSupabaseToken(accessToken: string): Promise<void> {
  const { data } = await api.post<AuthTokens>("/auth/supabase", { access_token: accessToken });
  tokenStore.set(data.access_token, data.refresh_token);
}
