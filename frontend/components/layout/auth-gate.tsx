"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { isAuthenticated } from "@/lib/auth";

export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    setReady(true);
  }, [router]);

  if (!ready) {
    return (
      <div className="flex min-h-full items-center justify-center text-sm text-slate-500">
        Loading workspace...
      </div>
    );
  }

  return children;
}
