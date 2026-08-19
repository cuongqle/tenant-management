"use client";

import Link from "next/link";
import { FormEvent, Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { register } from "@/hooks/use-auth";
import { safeNextPath } from "@/lib/auth";
import { emptyToNull } from "@/lib/utils";

function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = safeNextPath(searchParams.get("next"));
  const [name, setName] = useState("");
  const [email, setEmail] = useState(searchParams.get("email") ?? "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register({
        email,
        name: emptyToNull(name),
        password,
      });
      router.push(nextPath);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to register");
    } finally {
      setLoading(false);
    }
  }

  const loginHref =
    searchParams.get("next") || searchParams.get("email")
      ? `/login?email=${encodeURIComponent(email)}&next=${encodeURIComponent(nextPath)}`
      : "/login";

  return (
    <Card className="border-white/10 bg-white/95 p-8 shadow-2xl shadow-indigo-950/40 backdrop-blur">
      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">
        TenantMng
      </p>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Create account</h1>
      <p className="mb-6 text-sm text-slate-500">
        Register to manage organizations, projects, and environments.
      </p>
      <form className="flex flex-col gap-4" onSubmit={onSubmit}>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            name="name"
            placeholder="Admin"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            name="email"
            placeholder="you@example.com"
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
            name="password"
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </div>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <Button className="w-full" size="lg" type="submit" disabled={loading}>
          {loading ? "Creating account..." : "Register"}
        </Button>
      </form>
      <p className="mt-4 text-sm text-slate-500">
        Already have an account?{" "}
        <Link href={loginHref} className="font-medium text-indigo-600">
          Sign in
        </Link>
      </p>
    </Card>
  );
}

export default function RegisterPage() {
  return (
    <Suspense>
      <RegisterForm />
    </Suspense>
  );
}
