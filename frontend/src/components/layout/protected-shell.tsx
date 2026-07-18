"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/layout/sidebar";
import { Navbar } from "@/components/layout/navbar";
import { Spinner } from "@/components/ui/spinner";
import { useCurrentUser } from "@/hooks/use-auth";
import { tokenStore } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";

export function ProtectedShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  useCurrentUser();
  const { user, initialized } = useAuthStore();

  React.useEffect(() => {
    if (typeof window !== "undefined" && !tokenStore.get()) {
      router.replace("/login");
    }
  }, [router]);

  React.useEffect(() => {
    if (initialized && !user && !tokenStore.get()) {
      router.replace("/login");
    }
  }, [initialized, user, router]);

  if (!initialized && tokenStore.get()) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner className="h-8 w-8 text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Sidebar />
      <div className="md:pl-64">
        <Navbar />
        <main className="p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}
