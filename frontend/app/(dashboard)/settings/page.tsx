"use client";

import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { clearAccessToken } from "@/lib/auth";

export default function SettingsPage() {
  const router = useRouter();

  function signOut() {
    clearAccessToken();
    router.push("/login");
  }

  return (
    <Card className="max-w-xl p-6">
      <h2 className="text-base font-semibold text-slate-900">Session</h2>
      <p className="mt-2 text-sm text-slate-500">
        You are signed in with a JWT stored in this browser. Signing out clears
        the local token.
      </p>
      <Button className="mt-4" variant="secondary" onClick={signOut}>
        Sign out
      </Button>
    </Card>
  );
}
