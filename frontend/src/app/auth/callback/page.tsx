"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Spinner } from "@/components/ui/spinner";
import { exchangeSupabaseToken } from "@/hooks/use-auth";
import { getSupabase } from "@/lib/supabase";

export default function AuthCallbackPage() {
  const router = useRouter();

  React.useEffect(() => {
    const run = async () => {
      const supabase = getSupabase();
      if (!supabase) {
        router.replace("/login");
        return;
      }
      const { data } = await supabase.auth.getSession();
      const accessToken = data.session?.access_token;
      if (!accessToken) {
        toast.error("Could not complete sign-in");
        router.replace("/login");
        return;
      }
      try {
        await exchangeSupabaseToken(accessToken);
        router.replace("/dashboard");
      } catch {
        toast.error("Sign-in failed");
        router.replace("/login");
      }
    };
    run();
  }, [router]);

  return (
    <div className="flex h-screen flex-col items-center justify-center gap-3">
      <Spinner className="h-8 w-8 text-primary" />
      <p className="text-muted-foreground">Completing sign-in…</p>
    </div>
  );
}
