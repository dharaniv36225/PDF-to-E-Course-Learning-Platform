"use client";

import * as React from "react";
import Link from "next/link";
import { toast } from "sonner";
import { GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { api, getApiErrorMessage } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [sent, setSent] = React.useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/auth/forgot-password", { email });
      setSent(true);
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-background to-primary/5 px-4">
      <div className="w-full max-w-md">
        <Link href="/" className="mb-6 flex items-center justify-center gap-2">
          <GraduationCap className="h-7 w-7 text-primary" />
          <span className="text-xl font-bold gradient-text">LearnPDF</span>
        </Link>
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Reset password</CardTitle>
            <CardDescription>We&apos;ll email you a reset link</CardDescription>
          </CardHeader>
          <CardContent>
            {sent ? (
              <div className="space-y-4 text-center">
                <p className="text-sm text-muted-foreground">
                  If an account exists for <span className="font-medium">{email}</span>, a reset link
                  has been sent.
                </p>
                <Link href="/login">
                  <Button variant="outline" className="w-full">Back to sign in</Button>
                </Link>
              </div>
            ) : (
              <form onSubmit={onSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? <Spinner /> : "Send reset link"}
                </Button>
                <p className="text-center text-sm text-muted-foreground">
                  <Link href="/login" className="text-primary hover:underline">
                    Back to sign in
                  </Link>
                </p>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
