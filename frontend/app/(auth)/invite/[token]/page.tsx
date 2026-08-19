"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { invitationsApi } from "@/lib/resources";
import { isAuthenticated, readAccessTokenClaims } from "@/lib/auth";
import type { InvitationPreview } from "@/types";

export default function InvitePage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = use(params);
  const router = useRouter();
  const [preview, setPreview] = useState<InvitationPreview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const [signedIn, setSignedIn] = useState(false);
  const [signedInEmail, setSignedInEmail] = useState<string | null>(null);

  useEffect(() => {
    setSignedIn(isAuthenticated());
    setSignedInEmail(readAccessTokenClaims()?.email ?? null);
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const item = await invitationsApi.preview(token);
        if (!cancelled) {
          setPreview(item);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Invitation not found");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [token]);

  async function onAccept() {
    setAccepting(true);
    setError(null);
    try {
      const member = await invitationsApi.accept(token);
      router.push(`/organizations/${member.organization_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not accept invitation");
    } finally {
      setAccepting(false);
    }
  }

  const next = `/invite/${token}`;
  const emailQuery = preview ? `email=${encodeURIComponent(preview.email)}&next=${encodeURIComponent(next)}` : `next=${encodeURIComponent(next)}`;
  const emailMatches =
    signedInEmail !== null &&
    preview !== null &&
    signedInEmail.toLowerCase() === preview.email.toLowerCase();

  return (
    <Card className="border-white/10 bg-white/95 p-8 shadow-2xl shadow-indigo-950/40 backdrop-blur">
      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">
        TenantMng
      </p>
      <h1 className="mb-1 text-2xl font-semibold text-slate-900">Organization invite</h1>
      {loading ? (
        <p className="mt-4 text-sm text-slate-500">Loading invitation...</p>
      ) : error && preview === null ? (
        <p className="mt-4 text-sm text-destructive">{error}</p>
      ) : preview === null ? (
        <p className="mt-4 text-sm text-destructive">Invitation not found.</p>
      ) : (
        <>
          <p className="mb-6 text-sm text-slate-500">
            You were invited to join <strong>{preview.organization_name}</strong> as{" "}
            <strong>{preview.role}</strong>.
          </p>
          {preview.accepted ? (
            <p className="text-sm text-slate-500">This invitation was already accepted.</p>
          ) : preview.expired ? (
            <p className="text-sm text-destructive">This invitation has expired.</p>
          ) : !signedIn ? (
            <div className="flex flex-col gap-3">
              <p className="text-sm text-slate-500">
                Sign in or register with <strong>{preview.email}</strong> to accept.
              </p>
              <Button asChild>
                <Link href={`/login?${emailQuery}`}>Sign in</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href={`/register?${emailQuery}`}>Register</Link>
              </Button>
            </div>
          ) : !emailMatches ? (
            <p className="text-sm text-destructive">
              This invitation was sent to {preview.email}. Sign in with that email to
              accept.
            </p>
          ) : (
            <div className="flex flex-col gap-3">
              {error ? <p className="text-sm text-destructive">{error}</p> : null}
              <Button onClick={() => void onAccept()} disabled={accepting}>
                {accepting ? "Joining..." : "Accept invitation"}
              </Button>
            </div>
          )}
        </>
      )}
    </Card>
  );
}
