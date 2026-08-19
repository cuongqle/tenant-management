"use client";

import Link from "next/link";
import { FormEvent, Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login } from "@/hooks/use-auth";
import { safeNextPath } from "@/lib/auth";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = safeNextPath(searchParams.get("next"));
  const invitedEmail = searchParams.get("email");
  const [email, setEmail] = useState(invitedEmail ?? "admin@example.com");
  const [password, setPassword] = useState(invitedEmail ? "" : "Admin123!");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login({ email, password });
      router.push(nextPath);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in");
    } finally {
      setLoading(false);
    }
  }

  const registerHref = invitedEmail
    ? `/register?email=${encodeURIComponent(invitedEmail)}&next=${encodeURIComponent(nextPath)}`
    : "/register";

  return (
    <Card className="border-white/10 bg-white/95 p-8 shadow-2xl shadow-indigo-950/40 backdrop-blur">
      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">
        TenantMng
      </p>
      <h1 className="mb-1 text-2xl font-semibold text-slate-900">Welcome back</h1>
      <p className="mb-6 text-sm text-slate-500">
        Sign in to manage organizations, projects, and environments.
      </p>
      <form className="flex flex-col gap-4" onSubmit={onSubmit}>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </div>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <Button className="w-full" size="lg" type="submit" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </Button>
      </form>
      <p className="mt-4 text-sm text-slate-500">
        Need an account?{" "}
        <Link href={registerHref} className="font-medium text-indigo-600">
          Register
        </Link>
      </p>
    </Card>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}
